#!/usr/bin/env python3
"""Convert an Anki .apkg/.colpkg export into a two-column text file for Gizmo.

Output is one card per line: front <TAB> back.

Usage:
    python3 apkg_to_txt.py INPUT.apkg -o OUTPUT.txt [options]

Options:
    -o, --output PATH     output file (default: <input stem>_gizmo.txt)
    --delimiter STR       column separator: tab (default), semicolon, pipe, dash, comma
    --flip                cloze cards become definition -> answer instead of
                          blanked-sentence -> answer
    --deck SUBSTRING      keep only notes whose deck name contains SUBSTRING
    --tag TAG             keep only notes carrying TAG
    --blank STR           placeholder for the deleted span (default: ______)
    --keep-duplicates     do not drop identical front/back pairs
    --report              print a per-note breakdown instead of just the summary
"""

import argparse
import html
import io
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile

# Anki writes cloze markers as {{c1::answer}} or {{c1::answer::hint}}.
# Hand-edited decks sometimes contain a single colon ({{c1:answer}}), which Anki
# silently fails to render — tolerate it so those notes are not lost.
CLOZE_RE = re.compile(r"\{\{c(\d+):{1,2}(.+?)(?:::(.+?))?\}\}", re.S)
IMG_RE = re.compile(r"<img[^>]*>", re.I)
SOUND_RE = re.compile(r"\[sound:[^\]]*\]", re.I)
BLOCK_END_RE = re.compile(
    r"(?i)</?\s*(div|p|li|ul|ol|tr|td|h[1-6]|blockquote)[^>]*>"
)
BR_RE = re.compile(r"(?i)<\s*br\s*/?>")

DELIMITERS = {
    "tab": "\t",
    "semicolon": "; ",
    "pipe": " | ",
    "dash": " - ",
    "comma": ", ",
}


# --------------------------------------------------------------------------- #
# Reading the collection out of the package
# --------------------------------------------------------------------------- #

COLLECTION_NAMES = ["collection.anki21b", "collection.anki21", "collection.anki2"]


def extract_collection(pkg_path, workdir):
    """Return a path to a plain SQLite collection extracted from the package."""
    with zipfile.ZipFile(pkg_path) as zf:
        names = set(zf.namelist())
        found = next((n for n in COLLECTION_NAMES if n in names), None)
        if not found:
            raise SystemExit(
                f"No Anki collection inside {os.path.basename(pkg_path)}. "
                f"Archive contains: {sorted(names)[:10]}"
            )
        raw = zf.read(found)
        media_count = 0
        if "media" in names:
            try:
                media_count = len(json.loads(zf.read("media").decode("utf-8")))
            except Exception:
                media_count = -1  # binary media map (new format); count unknown

    if found.endswith(".anki21b"):
        try:
            import zstandard
        except ImportError:
            raise SystemExit(
                "This package uses the newer compressed format (collection.anki21b) "
                "and needs the 'zstandard' module.\n"
                "Install it with:  pip install zstandard --break-system-packages\n"
                "Or re-export from Anki with 'Support older Anki versions' ticked."
            )
        raw = zstandard.ZstdDecompressor().decompress(raw, max_output_size=1 << 31)

    out = os.path.join(workdir, "collection.sqlite")
    with open(out, "wb") as fh:
        fh.write(raw)
    return out, media_count


def deck_names(conn):
    """Map deck id -> name across both the old (col.decks JSON) and new schemas."""
    names = {}
    try:
        raw = conn.execute("select decks from col").fetchone()[0]
        if raw:
            for did, deck in json.loads(raw).items():
                names[int(did)] = deck["name"].replace("\x1f", "::")
    except Exception:
        pass
    if not names:
        try:
            for did, name in conn.execute("select id, name from decks"):
                names[int(did)] = name.replace("\x1f", "::")
        except sqlite3.OperationalError:
            pass
    return names


# --------------------------------------------------------------------------- #
# Text cleanup
# --------------------------------------------------------------------------- #


def notetypes(conn):
    """Map note type id -> (name, [field names]) across both schemas."""
    out = {}
    try:
        raw = conn.execute("select models from col").fetchone()[0]
        if raw:
            for mid, model in json.loads(raw).items():
                out[int(mid)] = (model["name"], [f["name"] for f in model["flds"]])
    except Exception:
        pass
    if not out:
        try:
            names = dict(conn.execute("select id, name from notetypes"))
            for ntid, name in names.items():
                fields = [
                    r[0]
                    for r in conn.execute(
                        "select name from fields where ntid=? order by ord", (ntid,)
                    )
                ]
                out[int(ntid)] = (name, fields)
        except sqlite3.OperationalError:
            pass
    return out


def resolve_fields(spec, field_names):
    """Turn 'Word,IPA' or '1,4' into a list of 0-based field positions."""
    picked = []
    lowered = [n.lower() for n in field_names]
    for part in [p.strip() for p in spec.split(",") if p.strip()]:
        if part.isdigit():
            picked.append(int(part) - 1)
            continue
        matches = [i for i, n in enumerate(lowered) if part.lower() in n]
        if not matches:
            raise SystemExit(
                f"Field {part!r} not found. Available fields: {field_names}"
            )
        picked.append(matches[0])
    return picked


def clean(s, drop_media=True):
    """Flatten one Anki field into a single line of plain text."""
    if not s:
        return ""
    if drop_media:
        s = IMG_RE.sub(" ", s)
        s = SOUND_RE.sub(" ", s)
    s = BR_RE.sub(" ", s)
    s = BLOCK_END_RE.sub(" ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = s.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    # Collapse a stray space before a comma or period left behind by tag removal.
    # Leave ? ! : ; alone — French typography puts a space there on purpose, and
    # removing it would quietly rewrite every sentence in a French deck.
    s = re.sub(r"\s+([,.])", r"\1", s)
    return s.strip(" -–—:;")


def join_extras(parts):
    parts = [p for p in parts if p]
    return " — ".join(parts)


# --------------------------------------------------------------------------- #
# Note -> card conversion
# --------------------------------------------------------------------------- #


def cloze_field_index(fields):
    for i, f in enumerate(fields):
        if CLOZE_RE.search(f):
            return i
    return None


def render_cloze(text, target_idx, blank):
    """Blank out only the target cloze index; reveal every other one."""

    def sub(m):
        if int(m.group(1)) == target_idx:
            hint = m.group(3)
            return f"{blank} ({clean(hint)})" if hint else blank
        return m.group(2)

    return CLOZE_RE.sub(sub, text)


def reveal_all(text):
    return CLOZE_RE.sub(lambda m: m.group(2), text)


def note_to_cards(fields, blank, flip):
    """Turn one Anki note into a list of (front, back) pairs.

    A cloze note with c1 and c2 becomes two cards, exactly as Anki would
    generate them, so nothing silently collapses into a single card.
    """
    idx = cloze_field_index(fields)
    cards = []

    if idx is None:
        front = clean(fields[0])
        back = join_extras(clean(f) for f in fields[1:])
        if front and back:
            cards.append((front, back))
        return cards

    text = fields[idx]
    extras = join_extras([clean(f) for i, f in enumerate(fields) if i != idx])
    indices = sorted({int(m.group(1)) for m in CLOZE_RE.finditer(text)})
    revealed = clean(reveal_all(text))

    for n in indices:
        blanked = clean(render_cloze(text, n, blank))
        answers = [clean(m.group(2)) for m in CLOZE_RE.finditer(text) if int(m.group(1)) == n]
        answer = ", ".join(a for a in answers if a)
        if not answer:
            continue

        if flip:
            front = join_extras([extras, blanked]) if extras else blanked
            back = answer
        else:
            front = blanked
            back = revealed if revealed else answer
            if extras and extras.lower() != back.lower():
                back = join_extras([back, extras])

        if front and back:
            cards.append((front, back))
    return cards


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main():
    ap = argparse.ArgumentParser(description="Anki .apkg -> Gizmo-importable .txt")
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--delimiter", default="tab", choices=sorted(DELIMITERS))
    ap.add_argument("--flip", action="store_true")
    ap.add_argument("--deck")
    ap.add_argument("--tag")
    ap.add_argument("--blank", default="______")
    ap.add_argument("--keep-duplicates", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--list-fields", action="store_true",
                    help="print every note type with its field names and note count, then exit")
    ap.add_argument("--notetype", help="keep only notes of note types whose name contains this")
    ap.add_argument("--front-field", help="field name (or 1-based index) to use as the front")
    ap.add_argument("--back-fields", help="comma-separated field names or indices for the back")
    args = ap.parse_args()

    sep = DELIMITERS[args.delimiter]
    output = args.output or os.path.splitext(os.path.basename(args.input))[0] + "_gizmo.txt"

    with tempfile.TemporaryDirectory() as tmp:
        db_path, media_count = extract_collection(args.input, tmp)
        conn = sqlite3.connect(db_path)
        decks = deck_names(conn)
        types = notetypes(conn)

        if args.list_fields:
            counts = dict(conn.execute("select mid, count(*) from notes group by mid"))
            for mid, (name, fields) in sorted(
                types.items(), key=lambda kv: -counts.get(kv[0], 0)
            ):
                if not counts.get(mid):
                    continue
                print(f"{counts[mid]:6}  {name}")
                for i, f in enumerate(fields, start=1):
                    print(f"          {i}. {f}")
            conn.close()
            return

        note_decks = {}
        try:
            for nid, did in conn.execute("select nid, min(did) from cards group by nid"):
                note_decks[nid] = decks.get(did, "")
        except sqlite3.OperationalError:
            pass

        rows = conn.execute("select id, mid, flds, tags from notes order by id").fetchall()
        conn.close()

    cards, skipped, media_notes = [], [], 0
    seen = set()

    for nid, mid, flds, tags in rows:
        tags = (tags or "").strip()
        if args.tag and args.tag.lower() not in tags.lower():
            continue
        if args.deck and args.deck.lower() not in note_decks.get(nid, "").lower():
            continue

        type_name, field_names = types.get(mid, ("", []))
        if args.notetype and args.notetype.lower() not in type_name.lower():
            continue

        fields = flds.split("\x1f")
        if IMG_RE.search(flds) or SOUND_RE.search(flds):
            media_notes += 1

        if args.front_field or args.back_fields:
            names = field_names or [str(i + 1) for i in range(len(fields))]
            f_idx = resolve_fields(args.front_field or "1", names)[0]
            b_idx = resolve_fields(args.back_fields or "2", names)
            front = clean(fields[f_idx]) if f_idx < len(fields) else ""
            back = join_extras(clean(fields[i]) for i in b_idx if i < len(fields))
            produced = [(front, back)] if front and back else []
        else:
            produced = note_to_cards(fields, args.blank, args.flip)
        if not produced:
            skipped.append((nid, clean(fields[0])[:70]))
            continue

        for front, back in produced:
            key = (front.lower(), back.lower())
            if not args.keep_duplicates and key in seen:
                continue
            seen.add(key)
            cards.append((front, back))

    with open(output, "w", encoding="utf-8") as fh:
        for front, back in cards:
            fh.write(f"{front}{sep}{back}\n")

    print(f"notes read      : {len(rows)}")
    print(f"cards written   : {len(cards)}")
    print(f"output          : {output}  ({args.delimiter}-separated)")
    if media_notes:
        print(f"media stripped  : {media_notes} note(s) referenced images/audio (text kept)")
    if media_count == -1:
        print("media map       : new-format binary media map, not inspected")
    if skipped:
        print(f"skipped (empty) : {len(skipped)}")
        for nid, preview in skipped[:10]:
            print(f"  - note {nid}: {preview!r}")
    if args.report:
        print("\n--- first 10 cards ---")
        for front, back in cards[:10]:
            print(f"{front}  ||  {back}")


if __name__ == "__main__":
    main()
