# 组织识别判据补充资料

获取日期：2026年11月11日。本批次为第一轮之后的识别判据专题，新增四项原始文献，不构成整个复杂系统领域的第二轮系统综述。

| 编号 | 实际阅读材料 | 原文文件 | 版本与阅读位置 |
|---|---|---|---|
| L09 | Wimsatt，Reductionism and Its Heuristics，2006 | [PDF](L09-wimsatt/original-uchicago.pdf) | 大学存档副本；PDF 第 4、15–17 页，第 8 节 |
| L10 | Newman 与 Girvan，Finding and Evaluating Community Structure in Networks | [PDF](L10-newman-girvan-2004/original-arxiv.pdf) | 实际保存 2003 年 arXiv v1；相关期刊论文发表于 2004 年；PDF 第 1、7–8 页 |
| L11 | Pearl，Causal Inference in Statistics，2009 | [PDF](L11-pearl-2009/original.pdf) | 大学存档副本；§2.1–2.3、§3.2–3.2.1 |
| L12 | Fortunato 与 Barthélemy，Resolution Limit in Community Detection | [PDF](L12-fortunato-barthelemy/original.pdf) | 存档预印本页眉为 2006 年 v2，另有 2008 年排版日期；相关期刊论文发表于 2007 年；PDF 第 1–5 页 |

每项来源的 `metadata.json` 记录实际下载地址、文件校验值与阅读范围，`extracted.txt` 为辅助提取文本。完整文件清单见 [manifest.json](manifest.json)。

L09 最初尝试的是另一份回顾章节，未取得 PDF；最后采用的是不同题名的原作者论文，二者不能视为同一作品的版本。L10 的大学链接证书校验失败，改用 arXiv。失败信息保存在对应的 `attempt-*.json` 中，没有将失败网页标记成论文全文。

检索返回内容保存为 [search-01.json](search-01.json)、[search-02.json](search-02.json) 和 [search-03.json](search-03.json)。仅出现于搜索结果、未打开采用的材料不逐一获取全文。正文判断与选择理由见[阅读记录](../../../research/reviews/02-reading-notes.md)。

第一轮来源继续使用[原有归档](../round-01/README.md)，不重复下载。项目自行构造的例子保存于 `research/examples`，不混入原始资料。
