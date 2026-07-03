#!/usr/bin/env python3
"""Fail when a configured locale contains missing or fuzzy project messages."""

import re
from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parents[1]
failed = False
VISIBLE_TEXT = re.compile(r">\s*([A-Za-z][^<{]*?)\s*<")
BLOCK_TRANSLATE = re.compile(
    r"{%\s*blocktranslate\b.*?{%\s*endblocktranslate\s*%}", re.DOTALL
)
ALLOWED_LITERALS = {"Wine", "Cellar", "Github"}

for path in sorted((ROOT / "locale").glob("*/LC_MESSAGES/*.po")):
    catalog = polib.pofile(path)
    problems = [
        entry
        for entry in catalog
        if not entry.obsolete
        and entry.msgid
        and ("fuzzy" in entry.flags or not entry.translated())
    ]
    if problems:
        failed = True
        print(f"{path.relative_to(ROOT)}: {len(problems)} incomplete translation(s)")
        for entry in problems:
            state = "fuzzy" if "fuzzy" in entry.flags else "missing"
            print(f"  [{state}] {entry.msgid}")

if failed:
    raise SystemExit(1)

for template in sorted((ROOT / "wine_cellar").glob("**/*.html")):
    source = BLOCK_TRANSLATE.sub("", template.read_text())
    for line_number, line in enumerate(source.splitlines(), start=1):
        if "{% translate" in line:
            continue
        for match in VISIBLE_TEXT.finditer(line):
            text = match.group(1).strip()
            if text and text not in ALLOWED_LITERALS:
                failed = True
                print(
                    f"{template.relative_to(ROOT)}:{line_number}: "
                    f"unmarked visible text: {text}"
                )

if failed:
    raise SystemExit(1)

print("All translation catalogues are complete.")
