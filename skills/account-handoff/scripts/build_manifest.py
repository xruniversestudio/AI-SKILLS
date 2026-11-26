#!/usr/bin/env python3
"""Build the file manifest (Markdown) grouped by project, then conversation.

Usage:
    python3 -I build_manifest.py <rows.csv> --out <manifest.md> [--index <index.csv>]

Accepted CSV columns (any subset; header names are case-insensitive):
    file | attachment, project, conversation, date, link | url, type
Rows from extract_chats.py (links.csv: conversation, link, date) work as they are.
Rows with no link are marked "link not recoverable". Exact duplicates are dropped.
"""
import argparse
import csv
import sys
from collections import defaultdict

ALIASES = {
    "file": ("file", "attachment", "name", "title"),
    "project": ("project",),
    "conversation": ("conversation", "chat"),
    "date": ("date", "created"),
    "link": ("link", "url"),
    "type": ("type",),
}


def pick(row, key):
    for alias in ALIASES[key]:
        if alias in row and row[alias] and row[alias].strip():
            return row[alias].strip()
    return ""


GENERIC_SEGMENTS = {"edit", "view", "preview", "share", "d", "document", "spreadsheets",
                    "presentation", "file", "u", "0", "1", "artifact", "public", "artifacts", ""}


def name_from_link(url):
    """Readable stand-in name for a link that has no file name."""
    kind = "Claude artifact" if "claude.ai" in url else "Google file" if "google.com" in url else "Linked file"
    path = url.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    segments = [s for s in path.split("/")[3:] if s.lower() not in GENERIC_SEGMENTS]
    ident = segments[-1][:12] if segments else ""
    return ("%s %s" % (kind, ident)).strip()


def load_project_map(index_path):
    """conversation title -> project, from extract_chats.py's index.csv."""
    mapping = {}
    with open(index_path, "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("title") and r.get("project"):
                mapping[r["title"]] = r["project"]
    return mapping


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--index", help="index.csv from extract_chats.py, to fill the Project column")
    args = ap.parse_args()
    project_map = load_project_map(args.index) if args.index else {}

    with open(args.csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [{(k or "").strip().lower(): (v or "") for k, v in r.items()} for r in reader]

    seen, grouped = set(), defaultdict(lambda: defaultdict(list))
    for r in rows:
        item = {k: pick(r, k) for k in ALIASES}
        if not item["project"] and item["conversation"] in project_map:
            item["project"] = project_map[item["conversation"]]
        if not item["file"] and item["link"]:
            item["file"] = name_from_link(item["link"])
        key = (item["file"], item["link"], item["conversation"])
        if not (item["file"] or item["link"]) or key in seen:
            continue
        seen.add(key)
        grouped[item["project"] or "No project"][item["conversation"] or "Unknown conversation"].append(item)

    out = ["| File | Project | Conversation | Date | Link |", "|---|---|---|---|---|"]
    for project in sorted(grouped):
        for conversation in sorted(grouped[project]):
            for item in sorted(grouped[project][conversation], key=lambda x: (x["date"], x["file"])):
                link = item["link"] or "link not recoverable"
                out.append("| %s | %s | %s | %s | %s |" % (
                    cell(item["file"] or "(unnamed)"), cell(project), cell(conversation),
                    cell(item["date"]), cell(link)))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("Rows written: %d (from %d input rows) -> %s" % (len(out) - 2, len(rows), args.out))


if __name__ == "__main__":
    main()
