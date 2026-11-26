# What moves between Claude accounts

Checked against support.claude.com and third-party write-ups on 2026-11-24. These rules change; re-check the official articles before promising anything. Official articles: "Export your Claude data" (9450526), "Import and export your memory" (12123587), "Move your personal Claude account to a Team or Enterprise organization" (9267400), "How to create custom skills" (12512198).

| Thing | Personal to personal | Personal into Team or Enterprise (same email) |
|---|---|---|
| Conversations | Not transferable. The data export cannot be imported into another personal account. | Reported to migrate (third-party sources; confirm in the official article). |
| Data export file | Download only (Settings, Privacy; web or desktop, not iOS or Android). Link expires after 24 hours. Excludes the original files you uploaded. | Primary Owner exports the whole organization. |
| Memory | Move by text: export verbatim from the old account, import via Start import. Experimental. | Reported to migrate. |
| Projects (instructions, files) | No transfer. Recreate: paste instructions, re-upload files. | Reported to migrate. |
| Custom skills | No migration path. Save the SKILL.md or ZIP first. | Do not migrate. |
| Connector sign-ins | Revoked or account-bound. Sign in again. | Revoked. Sign in again. |
| Plugins, scheduled tasks | Reinstall and recreate. | Reinstall and recreate. |

## Consequences for this skill

- Knowledge moves; accounts do not. So the pack carries text: memory, instructions, skill source, digests, a manifest.
- Anything the user uploaded must come from the user's own copies.
- Skills must be re-zipped with the folder as the ZIP's top level, then enabled under Settings, Capabilities.
- Always verify after a restore; memory import may not incorporate everything.
