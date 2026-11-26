#!/usr/bin/env python3
"""Turn a Claude data export into a working set for writing chat digests.

Usage:
    python3 -I extract_chats.py <export.zip | export-folder | conversations.json> --out <dir>
            [--since YYYY-MM-DD] [--min-messages N] [--max-chars N]

Writes into <dir>:
    index.csv              one row per conversation (id, title, project, dates, size)
    conversations/*.md     one trimmed, secret-redacted transcript per conversation
    links.csv              claude.ai artifact and Google Drive/Docs links found in chats
    attachments.csv        names of files attached to messages, per conversation

The export format may change between releases, so every field is read defensively.
Nothing is extracted from the ZIP to disk except what this script writes itself.
Run with `python3 -I` so a stray module in the current folder is never imported.
"""
import argparse
import csv
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone

MAX_MEMBER_BYTES = 800 * 1024 * 1024  # refuse absurdly large members

SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
     "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "[REDACTED_KEY]"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "[REDACTED_KEY]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_KEY]"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}"), "Bearer [REDACTED]"),
    (re.compile(r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key)\b(\s*[:=]\s*)\S+"),
     r"\1\2[REDACTED]"),
]

LINK_RE = re.compile(
    r"https?://(?:claude\.ai/(?:artifact|public/artifacts|share|chat|project)[^\s)\]>\"']*"
    r"|(?:docs|drive|sheets|slides)\.google\.com/[^\s)\]>\"']*)"
)


def redact(text):
    for pattern, repl in SECRET_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def read_member(source, wanted):
    """Return parsed JSON for the file named `wanted`, or None if absent."""
    if os.path.isdir(source):
        path = os.path.join(source, wanted)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as z:
            for info in z.infolist():
                if os.path.basename(info.filename) == wanted and not info.is_dir():
                    if info.file_size > MAX_MEMBER_BYTES:
                        sys.exit("%s is too large to read safely." % wanted)
                    with z.open(info) as f:
                        return json.loads(f.read().decode("utf-8"))
        return None
    if os.path.isfile(source) and os.path.basename(source) == wanted:
        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def parse_date(value):
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def message_text(msg):
    text = msg.get("text")
    if isinstance(text, str) and text.strip():
        return text
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type", "text") == "text":
                t = block.get("text")
                if isinstance(t, str):
                    parts.append(t)
        return "\n".join(parts)
    return ""


def sender_name(msg):
    s = (msg.get("sender") or msg.get("role") or "").lower()
    if s in ("human", "user"):
        return "User"
    if s in ("assistant", "claude"):
        return "Claude"
    return s.capitalize() or "Unknown"


def attachment_names(msg):
    names = []
    for key in ("attachments", "files"):
        for item in msg.get(key) or []:
            if isinstance(item, dict):
                name = item.get("file_name") or item.get("name")
                if name:
                    names.append(str(name))
    return names


def slugify(title, limit=50):
    slug = re.sub(r"[^\w\-]+", "-", title or "untitled", flags=re.UNICODE).strip("-")
    return (slug[:limit] or "untitled").lower()


def trim(text, max_chars):
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    head = int(max_chars * 0.6)
    tail = max_chars - head
    omitted = len(text) - max_chars
    return text[:head] + "\n\n[... %d characters omitted ...]\n\n" % omitted + text[-tail:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="export ZIP, extracted folder, or conversations.json")
    ap.add_argument("--out", required=True, help="output directory (created if missing)")
    ap.add_argument("--since", help="only conversations updated on/after this date (YYYY-MM-DD)")
    ap.add_argument("--min-messages", type=int, default=2, help="skip chats shorter than this (default 2)")
    ap.add_argument("--max-chars", type=int, default=12000, help="trim each transcript to this size (default 12000, 0 = no limit)")
    args = ap.parse_args()

    conversations = read_member(args.source, "conversations.json")
    if conversations is None:
        sys.exit("conversations.json not found in %s" % args.source)
    if isinstance(conversations, dict):
        conversations = conversations.get("conversations") or conversations.get("data") or []

    project_names = {}
    projects = read_member(args.source, "projects.json")
    if isinstance(projects, list):
        for p in projects:
            if isinstance(p, dict) and p.get("uuid"):
                project_names[p["uuid"]] = p.get("name") or ""

    since = None
    if args.since:
        since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)

    conv_dir = os.path.join(args.out, "conversations")
    os.makedirs(conv_dir, exist_ok=True)

    index_rows, link_rows, attach_rows = [], [], []
    kept = 0

    for i, conv in enumerate(conversations, 1):
        if not isinstance(conv, dict):
            continue
        messages = conv.get("chat_messages") or conv.get("messages") or []
        if len(messages) < args.min_messages:
            continue
        updated = parse_date(conv.get("updated_at") or conv.get("created_at"))
        if since and updated and updated < since:
            continue

        title = conv.get("name") or conv.get("title") or "Untitled"
        created = parse_date(conv.get("created_at"))
        project = ""
        if isinstance(conv.get("project"), dict):
            project = conv["project"].get("name") or ""
        project = project or project_names.get(conv.get("project_uuid") or "", "")

        lines = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            body = redact(message_text(msg).strip())
            who = sender_name(msg)
            if body:
                lines.append("**%s:** %s" % (who, body))
            for url in LINK_RE.findall(body):
                link_rows.append([title, url, created.date().isoformat() if created else ""])
            for name in attachment_names(msg):
                attach_rows.append([title, name])

        transcript = trim("\n\n".join(lines), args.max_chars)
        kept += 1
        filename = "%04d-%s.md" % (kept, slugify(title))
        with open(os.path.join(conv_dir, filename), "w", encoding="utf-8") as f:
            f.write("# %s\n\n" % title)
            f.write("- Date: %s\n- Project: %s\n- Messages: %d\n\n---\n\n"
                    % (created.date().isoformat() if created else "unknown", project or "none", len(messages)))
            f.write(transcript + "\n")

        index_rows.append([
            kept, conv.get("uuid") or "", title, project,
            created.date().isoformat() if created else "",
            updated.date().isoformat() if updated else "",
            len(messages), len(transcript), filename,
        ])

    with open(os.path.join(args.out, "index.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "uuid", "title", "project", "created", "updated", "messages", "chars", "file"])
        w.writerows(index_rows)
    with open(os.path.join(args.out, "links.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["conversation", "link", "date"])
        w.writerows(sorted(set(tuple(r) for r in link_rows)))
    with open(os.path.join(args.out, "attachments.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["conversation", "attachment"])
        w.writerows(sorted(set(tuple(r) for r in attach_rows)))

    print("Conversations in export: %d | kept: %d | links: %d | attachments: %d"
          % (len(conversations), kept, len(set(tuple(r) for r in link_rows)), len(set(tuple(r) for r in attach_rows))))
    print("Output: %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    main()
