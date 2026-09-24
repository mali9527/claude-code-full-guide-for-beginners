// Book-specific PDF layout. Text and indentation remain copyable.
#show raw.where(block: true): it => block(
  width: 100%, fill: rgb("#F5F6F3"), inset: 7pt,
  stroke: (left: 1pt + rgb("#CED8CD")), breakable: true,
)[
  #set text(font: ("Sarasa Mono SC", "PingFang SC"), size: 8pt)
  #set par(justify: false, leading: 0.5em)
  #for (i, line) in it.text.split("\n").enumerate() {
    if i > 0 { linebreak() }
    text(line)
  }
]
#show raw.where(block: false): it => text(font: ("Sarasa Mono SC", "PingFang SC"), size: 0.88em, it.text)
#show table: set text(size: 8.5pt)
#set table(inset: (x: 4pt, y: 4pt))
#show outline: it => { pagebreak(weak: true); it; pagebreak() }
#show link: set text(fill: rgb("#34724B"))
