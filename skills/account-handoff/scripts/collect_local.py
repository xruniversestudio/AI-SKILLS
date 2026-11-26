#!/usr/bin/env python3
"""Capture what Claude can read from its own workspace for a Context Pack.

Usage:
    python3 -I collect_local.py skills --list [--root DIR]
    python3 -I collect_local.py skills --names a,b --out DIR [--root DIR]
    python3 -I collect_local.py project [--dir /mnt/project] --out DIR

skills --list     Show skill folders found (name, files, size). Use ListSkills to tell
                  the user's own skills (ids starting "skill_") from built-in ones.
skills --names    Copy each named skill folder (all files) to DIR/skills/<name>/, zip it
                  with the folder as the ZIP's top level to DIR/skills/<name>.zip, scan it
                  for secrets, and print a Markdown block for pack section 4.
project           Copy project knowledge files (default /mnt/project, present only when the
                  chat runs inside a Claude Project) to DIR/project-files/ and print a
                  Markdown list for pack section 3.

Safety: symlinks are never followed, names are validated, per-file and total size limits
apply. Run with `python3 -I` so a stray module in the current folder is never imported.
"""
import argparse
import glob
import os
import re
import shutil
import sys
import zipfile

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 30 * 1024 * 1024
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-]{0,63}$")
TEXT_EXT = {".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".sh", ".html", ".css", ".csv", ".toml", ".ini", ".cfg"}

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("API key (sk-...)", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(r"\bghp_[A-Za-z0-9]{30,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
    ("credential assignment", re.compile(r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key)\b\s*[:=]\s*(?!\[REDACTED\])['\"]?[A-Za-z0-9/+_\-]{12,}")),
]


def default_skill_root():
    if os.path.isdir("/mnt/skills/user"):
        return "/mnt/skills/user"
    matches = sorted(glob.glob(os.path.expanduser("~/.claude/skills/synced/*")))
    return matches[0] if matches else None


def walk_files(root):
    """Yield (relative path, absolute path, size) for regular files; never follow symlinks."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not os.path.islink(os.path.join(dirpath, d)) and d != "__pycache__")
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            yield os.path.relpath(p, root), p, os.path.getsize(p)


def fence_for(text):
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(4, longest + 1)


def scan_secrets(root):
    warnings = []
    for rel, path, size in walk_files(root):
        if os.path.splitext(rel)[1].lower() not in TEXT_EXT or size > MAX_FILE_BYTES:
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                for label, pat in SECRET_PATTERNS:
                    if pat.search(line):
                        warnings.append("%s:%d looks like a secret (%s)" % (rel, lineno, label))
    return warnings


def cmd_skills(args):
    root = args.root or default_skill_root()
    if not root or not os.path.isdir(root):
        sys.exit("No skills folder found. Pass --root.")
    if args.list:
        for name in sorted(os.listdir(root)):
            d = os.path.join(root, name)
            if os.path.islink(d) or not os.path.isfile(os.path.join(d, "SKILL.md")):
                continue
            files = list(walk_files(d))
            print("%-32s files=%-3d bytes=%d" % (name, len(files), sum(s for _, _, s in files)))
        return
    if not args.names or not args.out:
        sys.exit("skills needs --list, or --names and --out")

    out_dir = os.path.join(args.out, "skills")
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for name in [n.strip() for n in args.names.split(",") if n.strip()]:
        if not NAME_RE.match(name):
            print("SKIP %r: invalid name" % name)
            continue
        src = os.path.join(root, name)
        if os.path.islink(src) or not os.path.isfile(os.path.join(src, "SKILL.md")):
            print("SKIP %s: no SKILL.md found under %s" % (name, root))
            continue
        files = list(walk_files(src))
        too_big = [rel for rel, _, size in files if size > MAX_FILE_BYTES]
        files = [(r, p, s) for r, p, s in files if s <= MAX_FILE_BYTES]
        total += sum(s for _, _, s in files)
        if total > MAX_TOTAL_BYTES:
            sys.exit("Total size over %d MB; split the capture." % (MAX_TOTAL_BYTES // 1024 // 1024))

        dest = os.path.join(out_dir, name)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        for rel, path, _ in files:
            target = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(path, target)
        zip_path = os.path.join(out_dir, name + ".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for rel, path, _ in files:
                z.write(path, os.path.join(name, rel))

        warnings = scan_secrets(dest)
        with open(os.path.join(dest, "SKILL.md"), "r", encoding="utf-8", errors="replace") as f:
            skill_md = f.read()
        fence = fence_for(skill_md)

        print("### %s\n" % name)
        print("- Files (%d): %s" % (len(files), ", ".join(rel for rel, _, _ in files)))
        print("- Full folder saved as: skills/%s.zip (folder is the ZIP's top level; upload under Settings, Capabilities)" % name)
        if too_big:
            print("- NOT captured (over 5 MB): %s" % ", ".join(too_big))
        for w in warnings:
            print("- WARN: %s" % w)
        print("\nFull SKILL.md (verbatim, so it can be rebuilt):\n")
        print(fence + "markdown")
        print(skill_md.rstrip("\n"))
        print(fence + "\n")
    print("Output folder: %s" % os.path.abspath(out_dir), file=sys.stderr)


def cmd_project(args):
    src = args.dir
    if not os.path.isdir(src):
        sys.exit("%s does not exist. This chat is probably not inside a Claude Project; run the project prompt inside each project instead." % src)
    if not args.out:
        sys.exit("project needs --out")
    out_dir = os.path.join(args.out, "project-files")
    os.makedirs(out_dir, exist_ok=True)
    total, rows, skipped = 0, [], []
    for rel, path, size in walk_files(src):
        if size > MAX_FILE_BYTES or total + size > MAX_TOTAL_BYTES:
            skipped.append(rel)
            continue
        target = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(path, target)
        total += size
        rows.append((rel, size))
    print("- Knowledge files captured (%d):" % len(rows))
    for rel, size in rows:
        print("  - %s (%d bytes) — copy saved under project-files/" % (rel, size))
    if skipped:
        print("- NOT captured (too large or over the total limit): %s" % ", ".join(skipped))
    print("Output folder: %s" % os.path.abspath(out_dir), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("skills")
    s.add_argument("--root")
    s.add_argument("--list", action="store_true")
    s.add_argument("--names")
    s.add_argument("--out")
    p = sub.add_parser("project")
    p.add_argument("--dir", default="/mnt/project")
    p.add_argument("--out")
    args = ap.parse_args()
    cmd_skills(args) if args.cmd == "skills" else cmd_project(args)


if __name__ == "__main__":
    main()
