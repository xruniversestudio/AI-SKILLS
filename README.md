# AI Skills

A collection of Claude skills, each self-contained in its own folder. Download a ZIP, upload it in **Settings > Capabilities**, and enable it.

| Skill | What it does | Download | Docs |
|---|---|---|---|
| `account-handoff` | Move to a new Claude account without starting from zero: builds a portable Context Pack (memory, project instructions, own skills, connectors, chat digests, file manifest) and restores it | [account-handoff.zip](downloads/account-handoff.zip) | [docs](docs/account-handoff.md) |

> Unofficial community skills. Not affiliated with or endorsed by Anthropic.

## Install a skill

1. Download the skill's ZIP from the table (`downloads/` is the only place ZIPs live).
2. In Claude: **Settings > Capabilities**, upload the ZIP, enable it.

## Layout

```
skills/<skill-name>/        the skills themselves (what Claude loads)
  SKILL.md                  folder name = `name` in this file
  references/  scripts/     optional helpers that belong to that skill only
docs/<skill-name>.md        human-readable docs per skill
downloads/<skill-name>.zip  upload-ready ZIPs, generated, never edited by hand
tools/build_zips.py         repo maintenance: rebuilds downloads/ from skills/
```

Python files live in two kinds of places: `skills/*/scripts/` are helpers a skill runs inside Claude; `tools/` is for maintaining this repository.

## Add a new skill

1. Create `skills/<new-skill>/SKILL.md` (frontmatter `name` must equal the folder name).
2. Run `python3 tools/build_zips.py` (rebuilds `downloads/`).
3. Add a row to the table above and a page in `docs/`.

## License

MIT, see [LICENSE](LICENSE).

---

## بالعربي

مجموعة مهارات (Skills) لـ Claude، كل مهارة بمجلدها وملفاتها المستقلة. نزّل ملف ZIP للمهارة، وافتح **Settings > Capabilities**، ارفعه وفعّله.

| المهارة | شو بتعمل | التنزيل |
|---|---|---|
| `account-handoff` | نقل معرفتك لحساب Claude جديد بدون ما تبدأ من الصفر (ذاكرة، تعليمات المشاريع، المهارات، الـ connectors، خلاصات المحادثات) | [account-handoff.zip](downloads/account-handoff.zip) |

لإضافة مهارة جديدة: أنشئ `skills/<الاسم>/SKILL.md` (اسم المجلد = حقل `name`)، شغّل `python3 tools/build_zips.py` (بيحدّث `downloads/`)، وأضف سطراً بالجدول.
