#!/usr/bin/env python3
"""Check a Context Pack before it is saved or imported.

Usage:
    python3 -I validate_pack.py <pack.md>

ERRORS (exit code 1): missing numbered sections 1-8, secrets, card-number-like digits.
WARNINGS: instruction-like text, oversized memory section, links, emails.
The pack is only read, never modified or executed.
"""
import re
import sys

REQUIRED_SECTIONS = {
    1: "Identity and working instructions",
    2: "Memory",
    3: "Projects",
    4: "Custom skills",
    5: "Connectors, plugins, scheduled tasks",
    6: "Chat digests",
    7: "File manifest",
    8: "Open threads",
}

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("API key (sk-...)", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(r"\bghp_[A-Za-z0-9]{30,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
    ("credential assignment", re.compile(r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key)\b\s*[:=]\s*(?!\[REDACTED\])['\"]?[A-Za-z0-9/+_\-]{12,}")),
]

INSTRUCTION_PATTERNS = [
    re.compile(r"(?i)ignore (all |any )?(previous|prior|above) (instructions|rules)"),
    re.compile(r"(?i)\byou (must|should) always (agree|praise|comply)"),
    re.compile(r"(?i)\bnever (criticize|disagree|push back)"),
    re.compile(r"(?i)\b(system prompt|developer message)\b"),
    re.compile(r"(?i)\bpretend (to be|you are)\b"),
]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://\S+")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ \-]?){13,19}(?!\d)")
MEMORY_LIMIT_BYTES = 60 * 1024


def luhn_ok(digits):
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def split_sections(text):
    """Return {number: body} for headings like '## 2. Memory'."""
    sections, current, buf = {}, None, []
    fence = None  # (char, length) of the currently open fenced block
    for line in text.splitlines():
        # headings inside fenced blocks (e.g. a pasted SKILL.md) are content, not sections
        fm = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fm:
            marker = fm.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif (marker[0] == fence[0] and len(marker) >= fence[1]
                  and not line.strip()[len(marker):].strip()):
                fence = None
            if current is not None:
                buf.append(line)
            continue
        if fence is not None:
            if current is not None:
                buf.append(line)
            continue
        m = re.match(r"^##\s+(\d+)\.\s+", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf)
            current, buf = int(m.group(1)), []
        elif re.match(r"^#\s+", line) and current is not None:
            sections[current] = "\n".join(buf)
            current, buf = None, []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    errors, warnings = [], []
    sections = split_sections(text)

    for num, name in REQUIRED_SECTIONS.items():
        if num not in sections:
            errors.append("missing section %d (%s)" % (num, name))

    for lineno, line in enumerate(text.splitlines(), 1):
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                errors.append("line %d: looks like a secret (%s)" % (lineno, label))
        for m in CARD_RE.finditer(line):
            digits = re.sub(r"\D", "", m.group(0))
            if 13 <= len(digits) <= 19 and luhn_ok(digits):
                errors.append("line %d: card-number-like digits" % lineno)
        for pattern in INSTRUCTION_PATTERNS:
            if pattern.search(line):
                warnings.append("line %d: instruction-like text; will be skipped on restore" % lineno)
                break

    memory = sections.get(2, "")
    mem_bytes = len(memory.encode("utf-8"))
    if mem_bytes > MEMORY_LIMIT_BYTES:
        warnings.append("memory section is %d KB; split it for import (limit about 64 KB)" % (mem_bytes // 1024))

    emails = set(EMAIL_RE.findall(text))
    urls = set(URL_RE.findall(text))
    if emails:
        warnings.append("%d email address(es) in the pack; confirm they should be there" % len(emails))
    if urls:
        warnings.append("%d link(s) in the pack; links are never followed during restore" % len(urls))

    for e in errors:
        print("ERROR  " + e)
    for w in warnings:
        print("WARN   " + w)

    mem_lines = len([l for l in memory.splitlines() if l.strip().startswith("- ")])
    print("Summary: %d error(s), %d warning(s) | memory lines: %d | sections found: %d/8"
          % (len(errors), len(warnings), mem_lines, len([n for n in REQUIRED_SECTIONS if n in sections])))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
