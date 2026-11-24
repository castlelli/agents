---
name: project-to-notes
description: Turn a Claude Project (or a long planning conversation) into Second Brain material — a set of atomic notes plus one project page, built strictly from the user's Obsidian templates, packaged for download, with a ready-to-paste Claude Code prompt that files them into the vault. Use whenever the user asks to transfer, export, move, archive or "map" a project or conversation into their second brain, Obsidian vault, PARA system or notes — including phrasings like "passa esse projeto pro second brain", "transforma isso em notas", "mapeia tudo que conversamos em notas atômicas", or "create a project page for this" — even if they don't mention templates or Claude Code.
---

# Project → Second Brain notes

The user keeps an Obsidian vault organized with PARA. This skill takes everything known about a Claude Project and turns it into files that drop straight into that vault: several atomic notes and one project page that ties them together. A separate Claude Code session later files them into the vault, so this skill produces clean, self-contained files and a prompt for that session — it does not decide tags, areas or links.

## 1. Gather the material

Collect everything the project contains before writing anything, because notes built from a partial read silently lose decisions:

- the Project's memory files (overview, ways-of-working, any area files inside the Project subtree), read in one call;
- files in `/mnt/project/` and any transcripts in `/mnt/transcripts/`;
- the current conversation.

Use only what the user actually said or decided. If the record is a summary rather than full conversations, say so in the final message, and never invent specifics (numbers, countries, dates) to make a note feel complete. Where sources conflict, write the neutral version and flag the conflict in one line.

## 2. Split into atomic notes

One note = one concrete subject someone could look up on its own: a decision and its reasons, a constraint and its consequences, a rule and how it applies, an option being evaluated. Aim for notes that are atomic but not thin — a note that is a single sentence should be merged into its neighbour; a note covering two independent decisions should be split. Typical projects yield 4–8 notes.

Open questions and next steps go in the project page's task list, not in their own notes. Each note may mention its own pending item briefly, if it's specific to that subject.

Write in the language of the conversation (usually Portuguese).

## 3. Name things short and intuitive

Titles are what the user types in Obsidian's quick switcher and what shows up in link lists, so they must be the words he'd search for — not a summary sentence.

- 2–4 words, noun phrase, no verbs of conclusion ("vence", "em vez de", "como restrição de").
- Use the project's own terms and acronyms (FUVEST, FCF, HST, DD).
- Don't prefix with the project name; the project page provides that context.
- Title must still be unambiguous inside a whole vault — add one qualifier if the bare term is generic ("Pós concomitante", not "Pós").
- Filename = title + `.md`.

| Too long | Better |
|---|---|
| Medicina na FMUSP em vez do HST Harvard-MIT | FMUSP vs HST |
| Trabalho como engenheiro no exterior antes da Medicina | Trabalho no exterior |
| FUVEST como restrição de sequenciamento para a FMUSP | Restrição do FUVEST |
| Pós-graduação stricto sensu concomitante à graduação na FMUSP | Pós concomitante |
| Aproveitamento de estudos da FMUSP na Farmácia da FCF-USP | Aproveitamento na FCF |

The project page is named after the Claude Project itself (e.g. `Medengineer`).

## 4. Follow the templates — always

The templates in `assets/` are the user's real Obsidian templates. Every file must start from a byte-for-byte copy of one of them, because his vault tooling and Claude Code's mapping step rely on that exact shape (including the two blank lines at the top, field order, heading levels and the tab before the Overview bullet).

- Atomic notes → `assets/full_note.md`
- Project page → `assets/project.md`

Build each file by copying the template with `cp` and then filling it; don't retype the header from memory. Substitute only:

- `{{date}}` → `YYYY-MM-DD`, `{{time}}` → `HH:MM`, in the user's local time (`TZ=America/Sao_Paulo date +"%Y-%m-%d %H:%M"` unless another zone is known).
- `{{title}}` → the note title.

Leave every other metadata field (`tags`, `parent project`, `area`, `status`, `deadline`) empty — those are assigned during vault integration, against the vault's existing values.

Body content:

- **Atomic note:** after `# Title`, write the note in prose with light `##` sections and short lists only where they help. Don't add new metadata fields or headings above the title.
- **Project page:** fill the three existing sections in place, keeping their headings and order.
  - `### Overview` — keep the tab-indented bullet style of the template. Say what the project is, where it stands, and mention every atomic note by title in italics (`*Restrição do FUVEST*`) where it fits the narrative.
  - `### Goals` — the project's durable goals as bullets.
  - `### Tasks and steps` — open items as `- [ ]` checkboxes.
- No wikilinks anywhere. Linking is the integration step's job.

## 5. Validate and deliver

Run the checker on the output folder; fix anything it reports before presenting:

```bash
python /path/to/skill/scripts/check_templates.py <output-folder> --project "<Project page filename>"
```

Then zip the folder, and call `present_files` with the zip first and each `.md` after it (project page first).

## 6. Hand-off prompt for Claude Code

End the reply with a paste-ready prompt built from `references/claude-code-prompt.md`, filled with the actual file list. The prompt must not tell Claude Code which links to make or what mapping logic to use — only the starting state, the goal, the safety limits and the report it should return.

Final message, in order: one or two sentences on what was produced, any caveats (summary-only source, conflicts found), the prompt block, and a one-line reminder to replace the bracketed paths and review the limits before pasting into an agent with filesystem access. Keep it short.
