#!/usr/bin/env python3
"""Build the PDF. Pipeline:

  1. Run preprocess.py (markdown → clean markdown with SVG refs)
  2. For each chapter, run `pandoc -f gfm -t typst` → pdf-build/chapters-typ/ch-XX.typ
  3. Write pdf-build/book.typ that stitches template + all chapters + part dividers
  4. Run `typst compile book.typ output/book.pdf`
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_BUILD = ROOT / "pdf-build"
MD_DIR = PDF_BUILD / "chapters-md"
TYP_DIR = PDF_BUILD / "chapters-typ"
TYP_DIR.mkdir(parents=True, exist_ok=True)
(PDF_BUILD / "output").mkdir(parents=True, exist_ok=True)

# Part structure: (title, [chapter-ids in order]) or None for front matter
PARTS = [
    (None,                       ["00"]),  # 前言 — no part divider
    ("第一部分 · 从零起步",      ["01", "02", "03", "04"]),
    ("第二部分 · 日常使用",      ["05", "06", "07", "08", "09", "10"]),
    ("第三部分 · 深度概念",      ["11", "12", "13", "14", "15"]),
    ("第四部分 · 避坑与判断力",  ["16", "17", "18", "19"]),
    ("第五部分 · 扩展能力",      ["20", "21", "22", "23", "24"]),
    ("第六部分 · 融入日常",      ["25", "26", "27"]),
    ("附录",                     ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]),
]

def run(cmd: list[str], **kw) -> None:
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kw)

def step1_preprocess() -> None:
    print("[1/4] preprocessing markdown…")
    run([sys.executable, str(PDF_BUILD / "preprocess.py")])

def step2_pandoc() -> None:
    print("[2/4] pandoc → typst per chapter…")
    for md in sorted(MD_DIR.glob("ch-*.md")):
        typ = TYP_DIR / (md.stem + ".typ")
        # -f gfm so task-list [ ] / [x] and tables work; -t typst is native
        run(["pandoc", "-f", "gfm+smart", "-t", "typst", str(md), "-o", str(typ)])
        # Post-process pandoc output: substitute symbols pandoc emits that
        # aren't native Typst (and that we don't want to depend on bindings for)
        text = typ.read_text(encoding="utf-8")
        text = text.replace(
            "#horizontalrule",
            '#align(center, line(length: 30%, stroke: 0.6pt + rgb("#D9D9D9")))',
        )
        # Pandoc wraps diagrams in `#box(image("…"))` — that's inline, so
        # `width: 100%` doesn't reach page width. Rewrite to a plain
        # `#image(..., width: 100%)` call which fills the content area.
        import re as _re
        text = _re.sub(
            r'#box\(image\("([^"]+)"\)\)',
            r'#image("\1", width: 100%)',
            text,
        )
        text = _re.sub(
            r'#image\("([^"]+)"\)(?!\s*,)',
            r'#image("\1", width: 100%)',
            text,
        )
        typ.write_text(text, encoding="utf-8")

def step3_stitch() -> None:
    print("[3/4] stitching book.typ…")
    parts_typ: list[str] = []
    for part_title, chap_ids in PARTS:
        if part_title is not None:
            parts_typ.append(part_divider(part_title))
        for cid in chap_ids:
            parts_typ.append(f'#include "chapters-typ/ch-{cid}.typ"')

    body = "\n\n".join(parts_typ)

    book_typ = f"""#import "template.typ": book, part-page, horizontalrule

#show: book.with(
  title: "Claude Code 零基础入门指南",
  subtitle: "针对 Claude Opus 4.7 全面更新",
  author: "马力（Ma Li）",
)

{body}
"""
    (PDF_BUILD / "book.typ").write_text(book_typ, encoding="utf-8")

def part_divider(title: str) -> str:
    return f'#part-page("{title}")'

def step4_typst() -> None:
    print("[4/4] typst compile…")
    out = PDF_BUILD / "output" / "Claude-Code-零基础入门指南.pdf"
    run(["typst", "compile", "--root", str(ROOT), str(PDF_BUILD / "book.typ"), str(out)])
    size_kb = out.stat().st_size / 1024
    print(f"\nPDF written: {out.relative_to(ROOT)} ({size_kb:.0f} KB)")

if __name__ == "__main__":
    step1_preprocess()
    step2_pandoc()
    step3_stitch()
    step4_typst()
