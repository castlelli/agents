---
name: anki-to-gizmo
description: Convert Anki decks (.apkg or .colpkg exports) into a plain two-column text file that Gizmo can import, handling cloze deletions, HTML markup, media references and both the legacy and the newer compressed collection formats. Use this skill whenever the user uploads or points at an .apkg/.colpkg file, mentions moving flashcards out of Anki, asks to turn a deck into a txt/csv/tsv, asks how to get an Anki deck into Gizmo, Quizlet, RemNote or any other flashcard app that imports two columns — and also when they ask to flatten, clean up or extract the contents of a deck, even if they never say the word "Gizmo".
compatibility: Needs Python 3 and a filesystem. The `zstandard` module is only required for packages exported by Anki 2.1.50+ without legacy support.
---

# Anki → Gizmo

Gizmo imports plain text where each line is one card: `front <TAB> back`. Anki
stores something much messier — HTML fragments, cloze markers, media tags,
a SQLite database inside a zip — so the job is to flatten that faithfully
without losing cards or leaking markup into the text.

## Workflow

1. **Inspect first.** `unzip -l deck.apkg` shows which collection file is inside
   (`collection.anki2`, `.anki21`, or the compressed `.anki21b`). This tells you
   immediately whether you'll need `zstandard`.
2. **Run the converter** in `scripts/apkg_to_txt.py`. It handles every format and
   note type; there is rarely a reason to write a one-off script instead.
3. **Read its summary output.** It reports notes read, cards written, media
   stripped and any skipped notes. If cards written is far below notes read, or
   notes were skipped, investigate before handing the file over — that gap is
   usually a real bug in the deck (empty fields, malformed cloze) worth telling
   the user about.
4. **Spot-check the file.** Look at a handful of lines, confirm every line has
   exactly two columns, and confirm no `{{c1::`, no `<div>`, no `&nbsp;` survived.
5. **Save to the outputs directory and present it**, then explain in one short
   paragraph how cloze cards were mapped, and mention the flip and delimiter
   options in case the user wants a different shape.

```bash
python3 scripts/apkg_to_txt.py deck.apkg -o /mnt/user-data/outputs/deck_gizmo.txt
```

If the package uses the compressed format, install the decompressor first:
`pip install zstandard --break-system-packages`. If that fails (no network),
tell the user to re-export from Anki with **"Support older Anki versions"**
ticked, which produces a plain `collection.anki2`.

## Options

| Flag | Effect |
| --- | --- |
| `-o PATH` | output path |
| `--delimiter tab\|semicolon\|pipe\|dash\|comma` | column separator; **tab is the default and is what Gizmo parses most reliably** |
| `--flip` | cloze cards become *definition → answer* instead of *blanked sentence → answer* |
| `--deck SUBSTRING` | keep only notes from decks whose name contains SUBSTRING |
| `--tag TAG` | keep only notes carrying TAG |
| `--notetype SUBSTRING` | keep only notes of matching note types |
| `--list-fields` | print every note type with its field names and note count, then exit |
| `--front-field NAME` | field to use as the front (name fragment or 1-based index) |
| `--back-fields A,B,C` | fields to join on the back, in order |
| `--blank STR` | placeholder for the deleted span (default `______`) |
| `--keep-duplicates` | keep identical front/back pairs instead of collapsing them |
| `--report` | print the first ten cards for a quick sanity check |

Big decks are often bundles of units or chapters. When the deck spans several
subdecks or tags and the user is studying one of them, offer `--deck` / `--tag`
rather than dumping everything into one Gizmo deck.

**Always run `--list-fields` first on a deck with more than a couple of thousand
notes.** Published language and exam courses are not flat word lists — they mix
a dozen note types, and the rich ones carry fields the learner never sees on the
card: entire dictionary articles, frequency indexes, per-voice audio, HTML
conjugation tables. The default mapping joins every non-empty field onto the
back, which turns those into thousand-character lines that are unusable in
Gizmo. `--list-fields` shows what is actually there in one screen; then pick the
two or three fields that carry the meaning with `--front-field` and
`--back-fields`. A good sanity check afterwards is the longest line in the file
(`awk '{print length}' out.txt | sort -rn | head -1`) — if it runs into the
thousands, a field slipped in that shouldn't have.

Producing two or three focused files (vocabulary, sentences) usually serves the
user better than one merged dump, since Gizmo decks are studied separately.

## How cards are mapped

**Cloze notes** — the default keeps the Anki study direction: the front is the
sentence with the deleted span replaced by `______`, the back is the same
sentence with the answer restored, plus any extra field appended after an
em dash. The surrounding context is the whole hint, which is why it belongs on
the front.

```
Anki:   Text = "{{c1::stifle}} a yawn"
        Back Extra = "to prevent something from being expressed"
Output: ______ a yawn ⇥ stifle a yawn — to prevent something from being expressed
```

`--flip` inverts this into a production drill — extra field and blanked sentence
on the front, the answer alone on the back. That suits vocabulary decks where
the goal is recalling the word from its meaning, and it also makes Gizmo's typed
answers usable, since the back is then a single short string. Offer it when the
deck is clearly vocabulary; the default is right for collocations and set
phrases, where the surrounding words are the thing being learned.

**Notes with several cloze indices** (`{{c1::…}}` and `{{c2::…}}` in one note)
become several cards, one per index, exactly as Anki generates them. The other
indices stay revealed so each card reads as a normal sentence. Collapsing them
into one card would silently lose material, so don't.

**Basic notes** map field 1 to the front and the remaining non-empty fields to
the back, joined with an em dash.

**Cloze hints** (`{{c1::answer::hint}}`) are kept in parentheses after the
blank, since Anki shows them on the front too.

## Details worth knowing

The converter identifies cloze notes by looking for `{{c…}}` markers in the
fields rather than by reading the note type. This matters because Anki's newer
schema stores note type configuration as protobuf that is painful to parse,
while the markers are unambiguous in every schema version.

It also tolerates `{{c1:answer}}` with a single colon. Anki fails to render
those, so hand-edited decks quietly carry dead cards that the user has never
seen — worth recovering, and worth mentioning when it happens.

**Media is dropped, text is kept.** `<img>` tags and `[sound:…]` references are
removed and the surrounding text survives, because a text file cannot carry the
media anyway. The summary counts how many notes were affected. If that count is
high, say so plainly — a deck that is mostly image-occlusion or audio cards will
lose its substance in this format, and the user should hear that before they
import rather than after.

**Duplicates collapse by default.** Anki decks accumulate identical notes; Gizmo
would import them as separate cards. Use `--keep-duplicates` if the user wants
a one-to-one mapping instead.

Everything is flattened to one line per card, since a stray newline inside a
field would split one card into two on import. Tabs inside fields are converted
to spaces for the same reason.

## Other targets

The same two-column output imports into Quizlet (paste, set the separator to
tab, rows to newline), RemNote and most other flashcard apps. If the user wants
a spreadsheet instead, `--delimiter comma` is not safe for text containing
commas — convert the tab file to a proper quoted CSV with `csv.writer` instead.
