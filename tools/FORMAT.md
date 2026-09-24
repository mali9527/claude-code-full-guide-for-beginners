# Studio 0.1 data and module contract

Python 3.9+. Dependencies: PyYAML, optional opencc-python-reimplemented for zh-TW.
All paths are relative to the book; work IDs and unit IDs are slugs.
Modules return dicts (JSON serializable); raise common.StudioError for actionable errors.
No network during check/build. Ordinary status doesn't build or fetch.

book.yaml:
  id: fixture-a
  title: 样例甲
  type: book | tutorial
  language: zh-CN
  product: example-a
  audience: 零基础普通人
  baseline: {product_version: fictional-1, checked_on: 2026-09-24}
  repository: {name: owner/repo, default_branch: main}
  is_test: true
  watershed: choose
  units:
    - id: intro
      title: 认识样例
      path: manuscript/intro.md
      section: popular | watershed | deep | appendix
      depth: 0
      prerequisites: []
      features: [files]
      facts: [example-price]
      required_checks: [editorial, facts] # optional; otherwise inherit book.required_checks
      derived_from: null | {id: terminal-basics, version: v1}
  outputs:
    combined: 全书.md
    readme: README.md
    pdf: {enabled: true, font: "PingFang SC", paper: a5}
    translations: {zh-TW: {enabled: true, directory: zh-TW}}
  diagrams: [{id: MM-01, unit: intro, type: mindmap}]
  protected_terms: [ExampleAI]\n  toolkit: 0.1.0
  published: {version: null, pdf: null}

facts.yaml is a LIST:
  - id: example-price
    claim: 虚构额度为 10
    scope: {product: example-a, plan: fictional}
    sources: [{url: "https://example.invalid/price", checked_on: "2026-09-24"}]
    checked_on: "2026-09-24"
    category: price | quota | account | install | startup | permission | undo | stable
    ttl_days: 90
    status: confirmed | unknown | changed | false
    critical: true

checks/*.yaml: a single record or list:
  unit: intro
  source_commit: full Git SHA of checked source (no self-reference)
  paths: [manuscript/intro.md]
  kind: editorial | facts | operations | trial
  result: pass | fail | unknown | not_applicable
  checked_on: "2026-09-24"
  engine: claude | codex | human
  author_engine: codex
  platforms: [mac]
  limitations: ""
  reason: ""

Public records never contain private report paths or names of trial participants.
book.required_checks default [editorial, facts, operations] per publish unit;
book.platforms default [mac]; tutorial may set appropriate required_checks.
Engine cross-review applies editorial; human override must include reason.

translations.yaml: mapping with entries list; builder owns exact details.
workspace.yaml:
  phase: M
  series: 普通人的 AI 工具入门系列
  works:
    - {id: fixture-a, path: tools/tests/fixtures/book-a, state: writing, is_test: true, priority: 1}
  candidates:
    - {id: claude-code, state: awaiting-P0}
  test_repositories: []
  records: private

Common API: load_yaml(path), atomic_write(path,text), safe_path(root,relative),
run_git(root,*args), git_commit(root,ref="HEAD"), slug(text), stripped_generated(text).
Check API: check_book(book_dir, publication=False, scope=None, today=None, freshness=True) -> {ok, issues:[{level,code,path,message}], summary:{...}}.
Build API (root-owned): build_book(book_dir, check_only=False, translate=False, pdf=False, source_ref=None, version=None, export_id=None) -> dict.
Release API is agent-owned; notify root once names are fixed; CLI wired by root.
Every agent writes only assigned files. Tests use unittest and temporary Git repos.
\ntranslations.yaml entries: unit, language, path, source_commit, source_sha256, converter, output_sha256, policy_sha256 (conversion terms and local patches), review (pending|pass).\ntranslation-overrides.yaml list: unit, language: zh-TW, anchor (optional unique context), expected (exactly once after anchor), replacement.\n

## 手绘插图字段（增量契约）

`diagrams` 增加可选字段 `spec`；`type: illustration` 时必须指向书仓内的 brief。原 `{id, unit, type}` 记录仍可用于历史图示。

```yaml
- id: FIG-001
  unit: intro
  type: illustration
  spec: assets/illustrations/FIG-001/brief.yaml
```

brief 的必需字段：`schema_version: 1`、`title`、`reader_question`、`takeaway`、`source_sections`（精确标题列表）、`placement`（精确标题）、`composition`、`content_guard`、`style`、`labels`（相对 brief 的 YAML 标签列表）。可选 `caption`、`source_ids`、`language_variants` 只作设计数据，不得据其手填值宣称已完成。

风格包路径为 `assets/illustrations/styles/<style>/`，保存 `style.md`、`prefix.txt`、`reference.png`、`paper.png`、`approval.json`。paper 是全书统一、不透明的细方格底稿；reference 是作者确认的完整效果图，两者不能混淆。

每次候选保存于 `revisions/rNN/`：`zh-CN.png`、`inputs.json`、`prompt.txt`、`provenance.json`、通过后的 `review.json`。来源快照的 fingerprint 包含 brief、标签、正文小节、单元所引事实、风格文件摘要和提示词摘要；自动导航及本系统的成对插图块不参加正文摘要。`selection.yaml` 只选择具体版本并记录相同的图片和输入摘要。

PNG 文件按真实格式、CRC、解压数据、不透明性与宽度（至少 1400 px）检查。机械尺寸通过不等于印刷或手机可读性通过；后者必须单独看实际版面。审校对象更换或输入过期均不得沿用旧的通过记录。

插图风格执行检查：公共前缀缺失（包括误写为 undefined）时不能制作生产包；所有采用图在 import/select/check/PDF 读取时解码检查透明度及颜色。彩色像素或明显色偏被拒绝；中性纸纹仅容许每通道 24/255 内的噪声，超过 12/255 的像素不得多于 0.5%。这不是把彩色图去色的转换。仍须人工检查笔触、纸底与文字。图内不得添加重复的界面版本注释。审校记录新增 monochrome: pass，不能只凭旧的 visual: pass 采用。
