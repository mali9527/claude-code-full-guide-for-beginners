// Claude Code 零基础入门指南 — A5 screen PDF template
// Typography: Source Han Serif SC (body) + Source Han Sans SC (headings) +
// JetBrains Mono / Sarasa Mono SC (code)

// macOS built-in Chinese fonts render reliably in Typst. Keep Source Han VF
// as fallback for cross-platform builds.
#let BODY-FONT = ("Songti SC", "Source Han Serif SC VF", "STSong")
#let HEADING-FONT = ("PingFang SC", "Source Han Sans SC VF", "Heiti SC")
#let MONO-FONT = ("JetBrains Mono", "Sarasa Mono SC", "Menlo")

#let ACCENT = rgb("#5C9F5C")        // green from README badges
#let ACCENT-WARM = rgb("#D5A021")   // warm gold from README badges
#let CODE-BG = rgb("#F6F6F4")
#let RULE = rgb("#D9D9D9")

// Pandoc emits `#horizontalrule` for thematic breaks (`---`).
// Define it as a thin rule centered horizontally.
#let horizontalrule = {
  v(0.4em)
  align(center, line(length: 30%, stroke: 0.6pt + RULE))
  v(0.4em)
}

// Part divider page — used between book parts
#let part-page(title) = {
  pagebreak(weak: true)
  set page(numbering: none, header: none)
  v(1fr)
  align(center, text(font: HEADING-FONT, size: 26pt, weight: "bold", title))
  v(2fr)
  pagebreak()
}

#let book(title: "", subtitle: "", author: "", body) = {
  // Page setup — A5 screen PDF, symmetric margins
  set page(
    paper: "a5",
    margin: (top: 18mm, bottom: 18mm, inside: 16mm, outside: 14mm),
    numbering: none,
    header: none,
  )

  set text(
    font: BODY-FONT,
    size: 10pt,
    lang: "zh",
    region: "cn",
    hyphenate: false,
  )

  set par(
    justify: true,
    leading: 0.78em,
    first-line-indent: 0pt,
    spacing: 0.9em,
  )

  // Headings use the sans family
  show heading: set text(font: HEADING-FONT, weight: "bold")

  // H1 = chapter: new page + generous vertical space
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(1.2em)
    block(below: 1.1em, text(size: 20pt, it.body))
    line(length: 36pt, stroke: 1.2pt + ACCENT)
    v(0.5em)
  }
  show heading.where(level: 2): it => {
    v(0.8em)
    block(below: 0.4em, text(size: 14pt, it.body))
  }
  show heading.where(level: 3): it => {
    v(0.5em)
    block(below: 0.3em, text(size: 12pt, it.body))
  }
  show heading.where(level: 4): it => {
    v(0.4em)
    block(below: 0.2em, text(size: 10.5pt, it.body))
  }

  // Inline code: tinted background, monospace
  show raw.where(block: false): it => box(
    fill: CODE-BG,
    inset: (x: 3pt, y: 1pt),
    outset: (y: 2pt),
    radius: 2pt,
    text(font: MONO-FONT, size: 0.9em, it),
  )

  // Block code: tinted background, padded
  show raw.where(block: true): it => block(
    fill: CODE-BG,
    stroke: (left: 2pt + RULE),
    inset: (x: 8pt, y: 7pt),
    radius: 2pt,
    width: 100%,
    breakable: true,
    text(font: MONO-FONT, size: 8.5pt, it),
  )

  // Tables: horizontal-only rules, tight padding
  show table: set table(
    stroke: (x, y) => (
      top: if y == 0 { 0.8pt + black } else if y == 1 { 0.4pt + RULE } else { none },
      bottom: 0.4pt + RULE,
      left: none, right: none,
    ),
    inset: (x: 5pt, y: 4pt),
  )

  // Links are green
  show link: set text(fill: ACCENT)

  // Blockquote styling
  show quote: it => block(
    stroke: (left: 2.5pt + ACCENT),
    inset: (left: 10pt, y: 3pt),
    text(style: "normal", it.body),
  )

  // Figure captions: smaller
  show figure.caption: set text(size: 8pt, fill: gray.darken(30%))
  show figure: it => {
    v(0.3em)
    align(center, it)
    v(0.3em)
  }

  // Images: preprocess.py wraps each pandoc image in
  //   #block(width: 100%, image("...", width: 100%))
  // so figures fill the content area. No additional show rule needed —
  // adding `show image: it => align(...)` would re-flow and drop width.

  //
  // —— FRONT MATTER ——
  //

  // Cover page — full-bleed image + title overlay at bottom
  set page(margin: 0pt)
  block(
    width: 100%,
    height: 100%,
    fill: white,
    align(center + horizon)[
      #image("../assets/cover.png", width: 100%)
    ],
  )
  pagebreak()

  // Title page
  set page(margin: (x: 16mm, y: 18mm))
  v(1fr)
  align(center)[
    #text(size: 22pt, font: HEADING-FONT, weight: "bold")[#title]
    #v(0.6em)
    #text(size: 13pt, font: HEADING-FONT, fill: gray.darken(20%))[#subtitle]
    #v(2em)
    #text(size: 12pt, font: HEADING-FONT)[#author]
  ]
  v(2fr)
  align(center)[
    #text(size: 9pt, fill: gray.darken(20%))[
      2026 · 首版 \
      github.com/mali9527/claude-code-full-guide-for-beginners
    ]
  ]
  pagebreak()

  // Copyright page
  v(1fr)
  text(size: 9pt)[
    *#title* · 首版 2026-04

    作者：马力（Ma Li） · \@mali9527 · li.ma.aria\@gmail.com

    GitHub 仓库：github.com/mali9527/claude-code-full-guide-for-beginners

    #v(0.4em)

    本书以 *CC BY-NC-SA 4.0* 协议开源。
    允许自由传播 / 修改 / 翻译，禁止商用，修改后须保持同样协议开源。
    详见 LICENSE 文件。

    #v(0.4em)

    本书内容针对 *Claude Opus 4.7* 全面更新（Anthropic 2026-04-16 发布）。
    后续版本迭代会同步修订，最新版本请访问 GitHub 仓库。
  ]
  pagebreak()

  // Table of contents
  show outline.entry.where(level: 1): it => {
    v(0.4em, weak: true)
    text(font: HEADING-FONT, weight: "bold", size: 10pt, it)
  }
  outline(title: [目录], depth: 2, indent: 1em)
  pagebreak()

  //
  // —— BODY ——
  //

  // Turn on page numbers for body
  set page(
    numbering: "1",
    number-align: center + bottom,
    header: context {
      let current = here().page()
      let all-h1 = query(heading.where(level: 1))
      let preceding = all-h1.filter(h => h.location().page() < current)
      let on-page = all-h1.filter(h => h.location().page() == current)
      // Show the ongoing chapter title only on pages that don't themselves
      // start a new chapter (chapter openers carry the big title already)
      if preceding.len() > 0 and on-page.len() == 0 {
        align(center, text(size: 8pt, fill: gray.darken(10%), preceding.last().body))
        v(-0.6em)
        line(length: 100%, stroke: 0.3pt + RULE)
      }
    },
  )
  counter(page).update(1)

  body
}
