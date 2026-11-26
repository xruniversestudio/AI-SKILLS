# AI Skills

A collection of Claude skills, each self-contained in its own folder. Download a ZIP, upload it in **Settings > Capabilities**, and enable it.

| Skill | What it does | Download | Docs |
|---|---|---|---|
| `account-handoff` | Move to a new Claude account without starting from zero: builds a portable Context Pack (memory, project instructions, own skills, connectors, chat digests, file manifest) and restores it | [account-handoff.zip](downloads/account-handoff.zip) | [docs](docs/account-handoff.md) |

> Unofficial community skills. Not affiliated with or endorsed by Anthropic.

## Install a skill

1. Download the skill's ZIP from the table (or run `python3 scripts/build_zips.py` to build all of them into `dist/`).
2. In Claude: **Settings > Capabilities**, upload the ZIP, enable it.

## Layout

```
skills/<skill-name>/        one folder per skill; the folder name equals `name` in SKILL.md
  SKILL.md
  references/  scripts/     optional, stay inside the skill folder
docs/<skill-name>.md        long-form docs for each skill
downloads/<skill-name>.zip  upload-ready ZIPs
scripts/build_zips.py       rebuilds the ZIPs (checks folder name = skill name)
```

## Add a new skill

1. Create `skills/<new-skill>/SKILL.md` (frontmatter `name` must equal the folder name).
2. Run `python3 scripts/build_zips.py`, then copy `dist/<new-skill>.zip` to `downloads/`.
3. Add a row to the table above and a page in `docs/`.

## License

MIT, see [LICENSE](LICENSE).

---

## بالعربي

مجموعة مهارات (Skills) لـ Claude، كل مهارة بمجلدها وملفاتها المستقلة. نزّل ملف ZIP للمهارة، وافتح **Settings > Capabilities**، ارفعه وفعّله.

| المهارة | شو بتعمل | التنزيل |
|---|---|---|
| `account-handoff` | نقل معرفتك لحساب Claude جديد بدون ما تبدأ من الصفر (ذاكرة، تعليمات المشاريع، المهارات، الـ connectors، خلاصات المحادثات) | [account-handoff.zip](downloads/account-handoff.zip) |

لإضافة مهارة جديدة: أنشئ `skills/<الاسم>/SKILL.md` (اسم المجلد = حقل `name`)، شغّل `python3 scripts/build_zips.py`، انسخ الـ ZIP إلى `downloads/`، وأضف سطراً بالجدول.
