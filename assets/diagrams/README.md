# 插图维护入口

插图 ID、所属单元与类型唯一登记在 [book.yaml](../../book.yaml) 的 diagrams 清单；正文在插图前使用 diagram 注释。README 的数量由同一清单生成，不再维护另一份手工表。

风格依据 [_style.md](_style.md)，新图使用 [_template-mindmap.md](_template-mindmap.md)。既有 MM-01—MM-46 的含义随正文修订，保留 ID；附录 D 的三张存量流程图以 FC-legacy 编号接入。已删除图的 ID 不复用。

新增图片只按当前已批准的类型与风格进行。修图后运行单书检查和构建，不能把历史 PDF 中的旧 PNG 当作新稿图示。
