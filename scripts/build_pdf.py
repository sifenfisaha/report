#!/usr/bin/env python3
"""Markdown or HTML -> A4 PDF in the house print style.

usage: build_pdf.py <in.md|in.html> <out.pdf> [--title T] [--meta "line"]...
                    [--footer F] [--paper a4|letter] [--keep-html]

Markdown is converted with tables, smart quotes and dashes; the body is wrapped
in assets/report.css with a title block (title + meta lines + rule) and rendered
by render_pdf.js (Playwright) with a running footer and page numbers. For
layouts the markdown cannot express (stacked table cells, SVG exhibits), pass an
HTML fragment or a whole document instead; a fragment gets the same wrapper.
"""
import argparse
import datetime
import html
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(HERE, "..", "assets", "report.css")

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--title", default=None)
ap.add_argument("--meta", action="append", default=[], help="a line under the title, e.g. 'Prepared by X · 6 October 2026'")
ap.add_argument("--footer", default=None, help="left footer text; default is the title and today's date")
ap.add_argument("--paper", default="a4", choices=["a4", "letter"])
ap.add_argument("--keep-html", action="store_true")
args = ap.parse_args()

src = open(args.src, encoding="utf-8").read()
title = args.title or os.path.splitext(os.path.basename(args.out))[0].replace("-", " ")

if args.src.lower().endswith(".md"):
    import markdown
    body = markdown.markdown(src, extensions=["tables", "sane_lists", "smarty", "fenced_code"])
else:
    body = src

if "<html" in body.lower():
    page = body
else:
    meta = "".join(f"<p class='meta'>{m}</p>" for m in args.meta)
    css = open(CSS, encoding="utf-8").read()
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{css}</style></head><body><h1>{html.escape(title)}</h1>{meta}<hr class='title'>{body}</body></html>")

html_path = os.path.splitext(args.out)[0] + ".html"
open(html_path, "w", encoding="utf-8").write(page)
footer = args.footer or f"{title} · {datetime.date.today():%-d %B %Y}"
subprocess.run(["node", os.path.join(HERE, "render_pdf.js"), html_path, args.out, footer, args.paper], check=True)
if not args.keep_html:
    os.remove(html_path)
try:
    info = subprocess.run(["pdfinfo", args.out], capture_output=True, text=True).stdout
    pages = next((l.split()[-1] for l in info.splitlines() if l.startswith("Pages")), "?")
    print(f"{args.out}: {pages} pages")
except FileNotFoundError:
    print(args.out)
