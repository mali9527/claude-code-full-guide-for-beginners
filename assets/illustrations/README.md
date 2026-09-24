# 手绘插图

全书使用细方格纸与黑色中性笔手绘。身份与单元唯一登记于 [book.yaml](../../book.yaml)，画风依据 [已确认样张](styles/notebook-pen-v1/reference.png) 与 [规范](styles/notebook-pen-v1/style.md)。

[查看全书 42 张插图](preview.html)，可切换页面宽度与手机宽度。预览不代表已完成正式 PDF 版式验收。

运行 `python tools/studio.py illustrations status` 查看从实物和摘要推导的当前状态。`pack` 输出提示词与输入快照，`import` 保存新候选，`select` 在核对内容、文字、视觉审校后切换正文引用。普通检查与构建不调用图像服务。

命令契约见 [工具说明](../../tools/README.md)。图中文字的繁体本地化单独审校，不能用正文自动转换冒充图片翻译。
