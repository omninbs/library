#!/usr/bin/env python3

import re
from pathlib import Path


def walk(d=Path(), depth=0):
    for p in sorted(d.glob("*.md")):
        if p.name.startswith("_"): continue
        m = re.search(r"^#\s+(.+)", p.read_text("utf-8"), re.MULTILINE)
        home = depth == 0 and p.name == "README.md"
        label, link = ("主页", "/") if home else (m and m[1] or p.stem, p.as_posix())
        yield "  " * depth + f"- [{label}]({link})"
        if (sub := d / p.stem).is_dir(): yield from walk(sub, depth + 1)


Path("_sidebar.md").write_text("\n".join(walk()) + "\n", "utf-8")
