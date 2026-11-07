#!/usr/bin/env python3

import argparse
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote


def subdir(d, p):
    stem = re.sub(r"^\d+\.\s*", "", p.stem)
    return next((d / x for x in (p.stem, stem) if (d / x).is_dir()), None)


def walk(d=Path(), depth=0):
    for p in sorted(d.glob("*.md"), key=lambda p: (p.name != "README.md", p.name)):
        if p.name.startswith("_"): continue
        m = re.search(r"^#\s+(.+)", p.read_text("utf-8"), re.MULTILINE)
        home = depth == 0 and p.name == "README.md"
        label, link = ("主页", "/") if home else (m and m[1] or p.stem, quote(p.as_posix()))
        yield "  " * depth + f"- [{label}]({link})"
        if s := subdir(d, p): yield from walk(s, depth + 1)


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
        print(f"serving at http://127.0.0.1:{args.port}/", flush=True)
        ThreadingHTTPServer(("127.0.0.1", args.port), Preview).serve_forever()
