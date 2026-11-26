#!/usr/bin/env python3
"""Build one upload-ready ZIP per skill into dist/.

Usage: python3 scripts/build_zips.py [skill-name ...]
Each ZIP has the skill folder as its top level, as Claude requires.
"""
import os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
DIST = os.path.join(ROOT, "dist")


def main():
    wanted = set(sys.argv[1:])
    os.makedirs(DIST, exist_ok=True)
    for name in sorted(os.listdir(SKILLS)):
        folder = os.path.join(SKILLS, name)
        skill_md = os.path.join(folder, "SKILL.md")
        if not os.path.isfile(skill_md) or (wanted and name not in wanted):
            continue
        head = open(skill_md, encoding="utf-8").read(2000)
        m = re.search(r'(?m)^name:\s*["\']?([^"\'\n]+)', head)
        if not m or m.group(1).strip() != name:
            sys.exit("ERROR: folder '%s' does not match name in SKILL.md" % name)
        out = os.path.join(DIST, name + ".zip")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for dp, dn, fn in os.walk(folder):
                dn[:] = [d for d in dn if d != "__pycache__"]
                for f in sorted(fn):
                    p = os.path.join(dp, f)
                    if os.path.islink(p):
                        continue
                    z.write(p, os.path.relpath(p, SKILLS))
        print("built", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
