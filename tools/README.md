# Studio 0.1.0 使用说明

Python 3.9+；依赖固定在 requirements.txt。从书仓根目录运行 python tools/studio.py，或加全局 --root。全局 --json 放在命令前。单书工具独立运行，不读取私有总控。

## 查看与检查

~~~sh
python tools/studio.py status
python tools/studio.py check
python tools/studio.py check --publication --units intro choose --language zh-CN
python tools/studio.py check --publication --language zh-TW
~~~

默认 check 输出结构问题和证据缺口；--publication 将所选单元需要的证据作为阻断条件。默认选择全部单元。单元可在 book.yaml 中用非空 required_checks 覆盖书级需求：纯概念单元可只需 editorial/facts，有操作承诺的单元必须保留 operations。变更此范围会使旧摘要待复核；非必需项可有理由地记 not_applicable，不能用 N/A 越过已声明必需项。状态汇总不构建、不开网络；总控模式只有显式 status --write-roadmap 才更新 ROADMAP 的作品受管区；其中证据数量只是登记概览，当前有效性以 check 为准。

检查记录的 source_commit 必须是可取得的源稿提交，paths 必须包含该单元正文。审校记录本身的后续提交不会自我失效，正文、相关配置与事实的变化会使记录需要复核。完整数据格式见 FORMAT.md。

## 构建与翻译

~~~sh
python tools/studio.py build
python tools/studio.py build --check
python tools/studio.py build --zh-tw
~~~

build 先检查权威输入，再在临时目录生成；最后只写配置的生成物与 studio:nav/toc/release 区域。人工介绍保留。受管区域或合订稿有人工修改时停止。缺少标记时人工定位插入，不能由脚本重写整章。

.studio/generated.json 是生成物的上次写入记录，应随源稿提交。它只保护生成内容，不判定事实正确。不要通过删除它来强制覆盖人工修改。

繁体需先在工作分支提交原稿；translations.yaml 记录来源、转换版本、文件摘要和审读状态。translation-overrides.yaml 支持 unit、language、可选唯一 anchor、expected、replacement。修订必须唯一命中，否则停止。未登记的译文手改保留现场，整理为规则后再合并。代码围栏、行内代码、路径、链接目标和 protected_terms 不转换。Mermaid 内的可见中文随代码保留，需要时用定位明确的修订规则转换图中文字，再审读。

翻译初稿标 pending；实际审读后才可把 review 改为 pass。源稿或结果变化会重新待审。简体发布不自动声明繁体已同步。

## PDF

仅明确要求时使用：

~~~sh
python tools/studio.py build --pdf --source v2026.09.1 --version v2026.09.1 --export-id 01
~~~

源提交中的 outputs.pdf.enabled 必须为 true。工具从 Git 固定快照构建，不读工作区未提交正文；输出 build/pdf/<正文版本>/<导出号>/，含 PDF 和 export.json。已有导出号拒绝覆盖。视觉审阅的结论需另行记录。

Mac 环境采用 Pandoc、Typst、中文字体；有 Mermaid 时使用锁定 Mermaid CLI。安装可选 Node 依赖：PUPPETEER_SKIP_DOWNLOAD=true npm ci --prefix tools，并将 STUDIO_CHROME 指向已安装 Chrome 可执行文件。独立安装的渲染器可通过 STUDIO_MMDC 指定。没有图的 Markdown 路径不加载这些工具。

## 发布

以下以独立书仓为例；私有记录必须在书仓外。先核对已授权范围，工具不会替代作者决定。

~~~sh
python tools/studio.py release prepare --records ../private/my-guide/releases --version v2026.09.1 --source HEAD --repo owner/repo --notes-file ../release-notes.md
python tools/studio.py release audit --plan ../private/my-guide/releases/v2026.09.1/plan.json --repo owner/repo
python tools/studio.py release publish --plan ../private/my-guide/releases/v2026.09.1/plan.json --repo owner/repo --account account-name --execute
python tools/studio.py release resume --plan ../private/my-guide/releases/v2026.09.1/plan.json --repo owner/repo --account account-name --execute
python tools/studio.py release entries --plan ../private/my-guide/releases/v2026.09.1/plan.json
~~~

总控模式在 action 后加作品 ID。prepare 要求干净书仓，并在固定提交重新做公开条件检查；清单冻结来源、范围、目标、说明与附件字节。附件使用 --asset，可重复。GitHub 默认不提升 latest；若本次授权含推荐版更新，prepare 时加 --promote --expected-latest 原标签。无原推荐时不传原标签。

publish/resume 通过 gh 已有登录调用 GitHub，要求明确 --repo/--account/--execute。测试作品与 M 阶段必须使用 workspace.yaml 的 test_repositories 允许清单；不把 fixtures 的占位 owner/repo 当真实目标。先让来源提交存在于指定远端，脚本本身不 push 分支。发布响应不明先 audit/resume，不重建附件。

entries 只在本地更新 book.yaml 与 README，要求可核对的公开回执；不会 push。已公开但入口失败应补入口，不能重传正式附件。较新入口已经存在时拒绝旧版本覆盖。

延后 PDF 用 --kind pdf --source-version v2026.09.1 --version pdf-v2026.09.1-01，--source 必须解析到正文标签同一个 C；不提升正文 latest。

## 工具升级

采用版本见 tools/TOOLKIT_VERSION，tools/toolkit-manifest.json 记录入库时各工具文件。先比较已采用版本、本地定制和新源；本地有定制时展示差异并建立升级任务，不能直接覆盖。总控的 tools/toolkit_diff.py 只做比较，没有升级写入动作。

升级后运行 check/build 与对应测试，确认本书规范差异，再更新采用版本。工具升级不自动更新产品事实或正文。
