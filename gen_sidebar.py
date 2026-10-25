#!/usr/bin/env python3

import argparse
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def walk(d=Path(), depth=0):
    for p in sorted(d.glob("*.md")):
        if p.name.startswith("_"): continue
        m = re.search(r"^#\s+(.+)", p.read_text("utf-8"), re.MULTILINE)
        home = depth == 0 and p.name == "README.md"
        label, link = ("主页", "/") if home else (m and m[1] or p.stem, p.as_posix())
        yield "  " * depth + f"- [{label}]({link})"
        if (sub := d / p.stem).is_dir(): yield from walk(sub, depth + 1)


def generate():
    Path("_sidebar.md").write_text("\n".join(walk()) + "\n", "utf-8")


class Preview(SimpleHTTPRequestHandler):
    def do_GET(self):
        generate(); super().do_GET()


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("command", nargs="?", choices=["serve"])
    cli.add_argument("-p", "--port", type=int, default=8000)
    args = cli.parse_args()

    generate()
    if args.command == "serve":
        ThreadingHTTPServer(("127.0.0.1", args.port), Preview).serve_forever()
