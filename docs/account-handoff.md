# account-handoff

[Back to all skills](../README.md)

A Claude skill that helps you **move to a new Claude account without starting from zero**.

Claude has no built-in way to move your chats between two personal accounts: a data export cannot be imported into another personal account, and custom skills, connector sign-ins and plugins do not follow a migration. What *can* move is knowledge. This skill gathers it into one portable Markdown file, the **Context Pack**, keeps it outside any single account, and replays it into the new one.

> Unofficial community skill. Not affiliated with or endorsed by Anthropic. Claude's export and import features change; the skill tells Claude to re-check the official help articles before promising anything.

العربية: [اقرأ الشرح بالعربي في الأسفل](#بالعربي).

## What it does

| Item | How it is handled |
|---|---|
| Memory | Copied verbatim into the pack; restored additively in the new account |
| Your own custom skills | Read from Claude's workspace; every file saved, each skill zipped ready to upload |
| Connectors | Listed with their state; each needs a fresh sign-in in the new account |
| Plugins | Listed with their purpose; re-enable them in the new account |
| The project the chat runs inside | Knowledge files copied and instructions recorded |
| Other projects | You run a short prompt in each (or paste the reply); the skill adds it to the pack |
| Old chats | Short digests (context, decisions, open items, files) built from the official data export |
| Files Claude produced | A manifest grouped by project and conversation; links that cannot be recovered are marked as such |

## What it cannot do

- Move chat history itself between personal accounts.
- Read other projects from outside them, or recover files you uploaded yourself. Keep your originals.
- Carry sign-ins. Connectors and plugins always need setting up again.
- Replace the official migration when it applies (for example personal account into a Team or Enterprise organization with the same email). Use that first, and this skill for what it does not carry.

## Install

1. Download [`account-handoff.zip`](../downloads/account-handoff.zip), or zip the `skills/account-handoff/` folder yourself (or run `python3 tools/build_zips.py`) so that the folder is the top level of the ZIP.
2. In Claude, go to **Settings > Capabilities**, upload the skill, and enable it.

Run `scripts/` on your own machine only if you want the helpers outside Claude; inside Claude it runs them for you.

## Use

In the **old** account:

```text
Use the account-handoff skill and prepare a Context Pack for moving to a new account. Save it to Drive.
```

Claude shows a short plan, asks whether any sensitive categories may be included (default: none), builds the pack, checks it for secrets, and saves it only after you agree.

In the **new** account, upload the skill, then:

```text
Use account-handoff and restore my Context Pack.
```

and give it the pack. It lists what it will import and what it will skip, waits for your go-ahead, and ends with a verification step so you can see what carried over.

To add one project to an existing pack, start the skill inside that project, or paste the reply of the project prompt in `skills/account-handoff/references/prompts.md` into a general chat and say "add this project to my pack".

## Modes

`EXPORT` (old account) · `RESTORE` (new account) · `ADD-PROJECT` (add or refresh one project in an existing pack) · `MANIFEST` (files grouped by conversation) · `DIGEST` (summaries from the data export).

## What is in the repository

```
skills/account-handoff/
  SKILL.md                    the skill itself
  references/
    pack-template.md          the eight-section Context Pack format
    prompts.md                copy-paste prompts (English and Arabic)
    what-moves.md             what transfers and what does not
    privacy-rules.md          what never goes into a pack
  scripts/
    collect_local.py          capture own skills and current project files
    extract_chats.py          turn the data export into digest-ready transcripts
    validate_pack.py          check a pack for secrets and missing sections
    build_manifest.py         build the file manifest
```

## Privacy and safety

- A pack is a dense summary of a person. Keep it somewhere private; the skill tells you who can see the Drive folder before it saves.
- Passwords, API keys, tokens, card numbers and ID numbers are never written into a pack, and `validate_pack.py` blocks them.
- Health, finances, immigration or legal matters, other people's private details and personality assessments are included only if you say so.
- When restoring, a pack is treated as data, never instructions. Text in it that tries to steer Claude is skipped and reported.
- Nothing is deleted or overwritten without your confirmation.

## Status and known limits

- The scripts were tested on synthetic data (including an Arabic title, secrets, links, symlinks and nested code fences). The data-export reader reads fields defensively because the export format is not documented as stable; **it has not been run on a real export yet**. If a field differs, adjust `extract_chats.py` and please open an issue.
- The restore flow has not been tested against a second real account.
- Whether a feature (memory import, skill upload, plugins) is available depends on your plan.

Official help articles to check before you start: [Export your Claude data](https://support.claude.com/en/articles/9450526-export-your-claude-data) and [Import and export your memory](https://support.claude.com/en/articles/12123587-importing-and-exporting-your-memory-from-chatgpt-and-other-ai-providers).

## Contributing

Issues and pull requests are welcome, especially a real export sample (with private content removed) so the reader can be tightened. Keep the privacy rules intact.

## License

MIT, see [LICENSE](../LICENSE).

---

## بالعربي

**account-handoff** مهارة لـ Claude تساعدك تنتقل لحساب جديد **بدون ما تبدأ من الصفر**.

Claude ما بنقل المحادثات بين حسابين شخصيين، وملف التصدير ما بينستورد بحساب ثاني، والـ skills وتسجيل دخول الـ connectors ما بيتبعوا الانتقال. اللي بينتقل فعلاً هو **المعرفة**، فالمهارة بتجمعها بملف Markdown واحد اسمه «حزمة السياق» (Context Pack)، بتحفظه خارج أي حساب، وبتعيد تحميله بالحساب الجديد.

**شو بتلتقط:** الذاكرة حرفياً، وكل الـ skills اللي أنشأتها بكل ملفاتها، وقائمة الـ connectors والـ plugins، وملفات المشروع المفتوح، وخلاصات المحادثات القديمة من ملف التصدير الرسمي، وسجل بالملفات اللي أنتجها Claude.

**شو ما بتقدر عليه:** نقل المحادثات نفسها، وقراءة المشاريع الأخرى من خارجها (بتشغّل برومبت قصير داخل كل مشروع)، واسترجاع الملفات اللي رفعتها بنفسك، ونقل تسجيل الدخول.

**التثبيت:** نزّل `downloads/account-handoff.zip`، وبـ Claude افتح **Settings > Capabilities** وارفعه وفعّله.

**الاستخدام:**
- بالحساب القديم: «استخدم مهارة account-handoff وجهّز حزمة سياق للانتقال لحساب جديد. احفظها على Drive.»
- بالحساب الجديد: ارفع المهارة، ثم: «استخدم account-handoff واستعد حزمة السياق.»

**الخصوصية:** الأسرار والأرقام الحساسة ما بتنكتب بالحزمة، والفئات الحساسة (صحة، مالية...) بتنضاف فقط إذا طلبت، وما بينحذف أو بيتبدل شي بدون موافقتك. الحزمة ملخص كثيف عنك، فاحفظها بمكان خاص.

**حدود معروفة:** السكربتات اتجرّبت على بيانات تجريبية، وما اتجرّب قارئ ملف التصدير على ملف حقيقي بعد، ولا الاستعادة على حساب ثانٍ حقيقي.
