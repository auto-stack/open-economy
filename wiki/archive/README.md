# 独立来源资料包

书稿、原创研究、模型和经检查的来源描述由Git管理。第三方原文、完整OCR、页面图像、原始对话与获取响应继续保留在本地原位置，并另存一个独立ZIP；它们不随公开仓库分发。

本轮清单见[source-package-manifest.json](source-package-manifest.json)，逐项记录1358个档案文件的相对路径、字节数与SHA256，同时记录ZIP本身的SHA256。资料包位于本地`.local-artifacts/open-economy-source-pack-2026-11-12.zip`，该目录被忽略；没有删除或迁移`wiki/raw`和`wiki/derived`中的原件。缓存不属于资料包。

清单连接的是原目录结构：`wiki/raw`、`wiki/derived`和`research`下的`inspection`。资料包可以包含Git已有的元数据，以保留各轮归档的完整上下文；同名文件恢复前应核对是否一致，不覆盖后来修改的研究资料。

## 仅取得Git仓库时

先阅读书稿及[书目目录](../index/SOURCES.md)，通过DOI、来源链接、版本、实际读页及校验信息定位文献。指向论文原件、整页OCR或扫描图的本地链接依赖可选资料包，未安装不代表文件损坏。历史审计中“原件存在”“OCR完成”的状态描述的是当时研究环境，不代表这些原文已经随Git公开。

检查命令：`python research/tools/repository-package.py check --mode tree --revision HEAD --output .local-artifacts/package-check.json`。它区分仓库必需目标、可选来源目标和已安装但校验失败的资料；缺少可选原件不会报告原件校验已完成。

## 持有本地来源资料包时

先核对ZIP校验值及清单，再在工作目录之外检查文件列表；确认相对路径后按需恢复至对应位置。检查程序只读取工作目录与清单，不自动解压或覆盖。资料包的本地保存和完整性校验，不意味着已经获得对所有内容的公开再分发许可。

资料包没有上传远端。它是本地独立归档副本，不是异地备份；未来AutoDown转换继续使用原件、来源记录与明确的派生文本地位。
