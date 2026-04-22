#!/usr/bin/env python3
"""Extract every Mermaid diagram from manuscript/*.md into pdf-build/diagrams/MM-XX.mmd.

Each diagram is identified by a leading `<!-- diagram: MM-NN -->` marker followed
by a fenced mermaid code block. After extraction, `render_mermaid.sh` turns each
.mmd into a standalone SVG via mmdc.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript"
DIAGRAMS = ROOT / "pdf-build" / "diagrams"
DIAGRAMS.mkdir(parents=True, exist_ok=True)

PATTERN = re.compile(
    r"<!--\s*diagram:\s*(MM-\d+)\s*-->\s*\n```mermaid\s*\n(.*?)\n```",
    re.DOTALL,
)

def main() -> int:
    collected: dict[str, tuple[str, Path]] = {}  # id → (body, src)
    for md in sorted(MANUSCRIPT.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in PATTERN.finditer(text):
            mm_id, body = m.group(1), m.group(2)
            if mm_id in collected:
                prev = collected[mm_id][1]
                print(f"  ⚠︎ duplicate {mm_id}: {prev.name} vs {md.name}", file=sys.stderr)
            collected[mm_id] = (body, md)

    for mm_id in sorted(collected):
        body, _ = collected[mm_id]
        out = DIAGRAMS / f"{mm_id}.mmd"
        out.write_text(body + "\n", encoding="utf-8")

    print(f"Extracted {len(collected)} diagrams → {DIAGRAMS}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
