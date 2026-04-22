#!/usr/bin/env python3
"""Clean each chapter's markdown before handing to Pandoc:

  - Strip the chapter-nav footer (web-only navigation)
  - Replace each `<!-- diagram: MM-XX --> ```mermaid ... ``` ` block with
    an image reference to the pre-rendered SVG
  - Collapse the diagram's preceding heading ("### 本章地图") since the
    figure itself already serves as the chapter opener
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_BUILD = ROOT / "pdf-build"
MANUSCRIPT = ROOT / "manuscript"
OUT_DIR = PDF_BUILD / "chapters-md"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Chapter order (matches the build_book.py order we use for the web build)
CHAPTERS = [
    ("00", "manuscript/00-前言/00-本书怎么读.md"),
    ("01", "manuscript/part1-从零起步/01-先把电脑准备好.md"),
    ("02", "manuscript/part1-从零起步/02-安装-Claude-Code.md"),
    ("03", "manuscript/part1-从零起步/03-你的第一次对话.md"),
    ("04", "manuscript/part1-从零起步/04-Claude-Code到底是什么.md"),
    ("05", "manuscript/part2-日常使用/05-让它读文件.md"),
    ("06", "manuscript/part2-日常使用/06-让它改文件.md"),
    ("07", "manuscript/part2-日常使用/07-让它跑命令加权限机制.md"),
    ("08", "manuscript/part2-日常使用/08-交互循环七步法.md"),
    ("09", "manuscript/part2-日常使用/09-计划模式与撤销.md"),
    ("10", "manuscript/part2-日常使用/10-信任校准.md"),
    ("11", "manuscript/part3-深度概念/11-你的数据去哪了.md"),
    ("12", "manuscript/part3-深度概念/12-Claude为什么会变糊涂.md"),
    ("13", "manuscript/part3-深度概念/13-三层记忆.md"),
    ("14", "manuscript/part3-深度概念/14-写好你的CLAUDE.md.md"),
    ("15", "manuscript/part3-深度概念/15-模型与成本.md"),
    ("16", "manuscript/part4-避坑与判断力/16-新手10大错误.md"),
    ("17", "manuscript/part4-避坑与判断力/17-什么时候该停下来.md"),
    ("18", "manuscript/part4-避坑与判断力/18-常用快捷命令全览.md"),
    ("19", "manuscript/part4-避坑与判断力/19-输入技巧.md"),
    ("20", "manuscript/part5-扩展能力/20-Skills入门.md"),
    ("21", "manuscript/part5-扩展能力/21-自定义Slash命令.md"),
    ("22", "manuscript/part5-扩展能力/22-Subagents入门.md"),
    ("23", "manuscript/part5-扩展能力/23-Hooks入门.md"),
    ("24", "manuscript/part5-扩展能力/24-MCP入门.md"),
    ("25", "manuscript/part6-融入日常/25-团队协作基础.md"),
    ("26", "manuscript/part6-融入日常/26-进阶能力速览.md"),
    ("27", "manuscript/part6-融入日常/27-下一步路线.md"),
    ("A", "manuscript/附录/A-Mac终端速查.md"),
    ("B", "manuscript/附录/B-Windows-PowerShell速查.md"),
    ("C", "manuscript/附录/C-Slash命令全表.md"),
    ("D", "manuscript/附录/D-决策流程图.md"),
    ("E", "manuscript/附录/E-FAQ.md"),
    ("F", "manuscript/附录/F-术语表.md"),
    ("G", "manuscript/附录/G-报错自救手册.md"),
    ("H", "manuscript/附录/H-桌面应用导览.md"),
    ("I", "manuscript/附录/I-延伸阅读.md"),
    ("J", "manuscript/附录/J-Opus-4.7新手指南.md"),
]

# Match ``### 本章地图（...）\n\n<!-- diagram: MM-XX -->\n```mermaid\n...\n``` ``
# The preceding heading line is optional; we strip the diagram + any heading above it titled 本章地图.
DIAGRAM_WITH_HEADING = re.compile(
    r"(?:^#{2,4}\s*本章地图[^\n]*\n+)?"
    r"<!--\s*diagram:\s*(MM-\d+)\s*-->\s*\n"
    r"```mermaid\s*\n.*?\n```",
    re.DOTALL | re.MULTILINE,
)

# Match a bare diagram (no preceding heading)
DIAGRAM_BARE = re.compile(
    r"<!--\s*diagram:\s*(MM-\d+)\s*-->\s*\n"
    r"```mermaid\s*\n.*?\n```",
    re.DOTALL,
)

# Strip nav footer: "---\n<!-- chapter-nav -->\n..." to EOF
NAV_FOOTER = re.compile(r"\n*---\n+<!--\s*chapter-nav\s*-->.*$", re.DOTALL)

def preprocess_chapter(md: str) -> str:
    md = NAV_FOOTER.sub("\n", md)
    # First pass: collapse "本章地图" heading + diagram into a single image
    def sub_with_heading(m: re.Match) -> str:
        mm_id = m.group(1)
        return f"![](../diagrams/{mm_id}.png)"
    md = DIAGRAM_WITH_HEADING.sub(sub_with_heading, md)
    # Second pass: any remaining diagrams (no heading)
    md = DIAGRAM_BARE.sub(lambda m: f"![](../diagrams/{m.group(1)}.png)", md)
    return md.rstrip() + "\n"

def main() -> int:
    count = 0
    for cid, rel in CHAPTERS:
        src = ROOT / rel
        out = OUT_DIR / f"ch-{cid}.md"
        text = src.read_text(encoding="utf-8")
        cleaned = preprocess_chapter(text)
        out.write_text(cleaned, encoding="utf-8")
        count += 1
    print(f"Pre-processed {count} chapters → {OUT_DIR}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
