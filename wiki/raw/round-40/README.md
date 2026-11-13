# 2024年稳态综述及引用路线资料归档

2026年11月13日，Asia/Shanghai。优先补取L196全文，并按参考文献、后续引用和作者资料入口收集材料，服务[2026资料综述0.2](../../../research/surveys/01-organization-maintenance/review-2026.md)。此前档案不覆盖，新增资料未写入framework-v0.1的旧来源ZIP。

## 作品与实际阅读

| 编号与作品 | 取得版本 | 实际使用范围 |
|---|---|---|
| L196 Bechtel／Bich2024，Situating homeostasis in organisms；DOI10.1113/JP286883 | [作者网站完整PDF](L196-bechtel-bich-2024/original.pdf)，18页，J.Physiol.0.0稿页1–18；与正式卷期6003–6020分开定位 | 重点核查稿页2–16的概念史、调节方案、整体维持与结论，目视核对稿页8图2、12图3和14–15的网络论证；未独立复现实验或逐条读完参考原文。沿用旧编号，不计作新作品 |
| L199 Billman2020，Homeostasis: The Underappreciated and Far Too Often Ignored Central Organizing Principle of Physiology；DOI10.3389/fphys.2020.00200 | [出版社PDF](L199-billman-2020/original.pdf)，12页 | PDF2定义／引言和11的Summary，选段；L196的后向参考路线 |
| L200 Bich／Menatti，Homeostasis and Health: From Balance to Change；DOI10.1007/s13752-025-00510-x | [作者保存的在线排版PDF](L200-bich-menatti-health/original.pdf)，13页；2025-10-14在线，2026卷21期2:174–186 | PDF1、7–8、10选段；引用L196的条目在PDF11；概念与医学哲学提案。稿页7脚注7的冬眠温度表述差异待回查，不用于书稿具体数值 |
| L201 Horseman2025，Kinorhesis；DOI10.3389/fphys.2025.1633607 | [出版社PDF](L201-horseman-2025/original.pdf)，15页，Hypothesis and Theory | PDF2–3、13选段；引用L196的条目在PDF14。用作保持与转变的比较，不视为统一演化定律 |
| L202 Farnsworth2025，Homeostatic set-points are physical and foundational to organism autonomy；DOI10.1016/j.biosystems.2025.105634 | [大学库PDF](L202-farnsworth-2025/original.pdf)，18页，含一页库封面；文件声明Publisher's PDF，与OpenAlex该位置的submittedVersion标记不同 | PDF2–3、12–13选段；正文页1＝PDF2；引用L196在PDF15。未独立重推代谢控制与动力学结论，保留作者更强论断的检验任务 |
| L203 Bechtel／Bich，Rediscovering Bernard and Cannon；DOI10.1017/psa.2024.72 | [作者保存的期刊PDF](L203-bechtel-bich-history/original.pdf)，22页，2024-12-12在线，2025卷92:584–605 | 仅首页摘要、日期与卷期身份；正文后续读。引用L196的关系目前只来自OpenAlex，未在本文参考文献逐条核实；不同作品，不是L196重印 |

共6份PDF，其中5个新增作品、L196同一作品的新完整副本；不以下载页数或候选数量计阅读量。各目录的metadata.json、download-log.json及read-scope-extension.json记录原网址、实际取得版本、读页和SHA-256。正文提取是检索辅助，关键位置以原文件和检查图为准。

## 引用追踪与发现记录

discovery/L196-crossref.json保存出版社提交的88条参考记录；discovery/L196-citing-openalex.json保存截至2026-11-13的34条引用候选，单次查询每页100条，实际返回34条。它们是不同集合和角色，不相加为纳入研究数。OpenAlex可能跨版本关联，候选的日期、撤回及真实引用关系另查。

向前候选包含一个WITHDRAWN题名，本轮不作为证据；一个首发日期显示2023的条目保留版本日期核查状态，不称作在2023年引用2024论文。L200–L202的引用关系已定位到实际PDF；L203仍为索引线索。2026相关候选列入下一批阅读队列。

作者发表目录保存在discovery/bich-publications.html，用于发现完整PDF及核对卷期日期。API、目录和网页回包与实际论文分开。第一组网页搜索回包未逐字保存，已在initial-query-notes.json记录原检索式及这一缺口；后续搜索／打开回包保存于search／open文件，不冒称全程逐字日志齐全。

PhilArchive直取403、HAL文档请求返回非PDF等尝试保留。最终作者PDF的成功不抹去先前失败，不将HTTP200的HTML当作原PDF。Partridge1982补到的PubMed原摘要仅作待办入口，未获得其正文、未分配新的采用作品编号。

既有L61 XML按原编号与原阅读范围复用，见[source-reuse.json](source-reuse.json)；本轮没有扩读该XML。旧第39批L196部分文字与元数据保留，实际本轮全文状态以本批为准。

分析见[阅读记录](../../../research/surveys/01-organization-maintenance/followup-2026-11-13/reading-notes.md)、[章节对应](../../../research/surveys/01-organization-maintenance/followup-2026-11-13/chapter-mapping.md)和[第45轮](../../../research/reviews/45-homeostasis-review-followup.md)。本批[manifest.json](manifest.json)列文件字节与SHA，不自包含。原件、提取、原始API回包和检查图按现有gitignore保存在本地，描述记录与原创研究可纳管；未执行新的提交、标签、推送或公开再分发。
