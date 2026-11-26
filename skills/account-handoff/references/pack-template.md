# Context Pack template

Copy this structure exactly. `scripts/validate_pack.py` checks that all eight numbered sections exist. Headers stay in English; content stays in the user's language. Every fact line starts with `- [stated]` when the user said it themselves.

````markdown
# Context Pack

- Created: YYYY-MM-DD
- Source account label: <a short label, e.g. "personal" or "work"; no email address>
- Language(s): <e.g. Arabic, English>
- Sensitive categories included: <none | list what the user explicitly approved>
- Built with: account-handoff skill

## 1. Identity and working instructions

Only what the user stated about themselves, plus rules they gave Claude. Verbatim where possible.

- [stated] Name: ...
- [stated] Role and employer: ...
- [stated] Location and working languages: ...
- [stated] Instruction: <e.g. "reply in Arabic, short answers on mobile">

## 2. Memory

Verbatim export from the old account's memory, one fact per line.

- [stated] ...

## 3. Projects

### <Project name>

- Purpose: ...
- Status: <active | paused | done> (as of YYYY-MM-DD)
- Key decisions: ...
- Knowledge files (originals are NOT in the data export; keep your own copies):
  - <file name> — original lives at: <path or link>

Project instructions (verbatim):

```text
<paste the project's instructions here>
```

## 4. Custom skills

### <skill-name>

- Files: <list from collect_local.py>
- Full folder saved as: skills/<name>.zip — Drive link: <link>

Full SKILL.md (verbatim, so it can be rebuilt; use a fence longer than any backticks inside):

```markdown
<paste SKILL.md here>
```

## 5. Connectors, plugins, scheduled tasks

Never record tokens or passwords. Each needs a fresh sign-in in the new account.

- [ ] <Connector> — state in old account: connected | needs_reconnect | connect_incomplete — used for: ... — needed for: <projects>
- [ ] <Plugin> — what it does: ... (re-enable in the new account; may depend on plan)
- [ ] <Scheduled task> — what it did and when: ... (or "check the Scheduled area in the app")

## 6. Chat digests

Grouped by project or topic, not by date. These are summaries, not transcripts.

### <Project or topic>

**<Chat title> (YYYY-MM-DD)**
- Context: ...
- Decisions: ...
- Open items: ...
- Files: <names, or "none">

## 7. File manifest

| File | Project | Conversation | Date | Link |
|---|---|---|---|---|
| ... | ... | ... | ... | <link or "link not recoverable"> |

## 8. Open threads

Work in progress that the next session should pick up.

- <What, where it stopped, next step>
````

## Notes for whoever fills it in

- Section 2 should be pasted as-is. Do not "clean up" the user's memory.
- Section 6 digests keep decisions and facts only. Drop pleasantries and dead ends.
- If a section has nothing, write `None.` rather than deleting the header.
- Keep section 2 under about 60 KB so it fits one memory import.
