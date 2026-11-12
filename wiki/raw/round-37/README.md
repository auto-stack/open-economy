# 融资原式复核与开放商业论证资料

日期：2026年11月12日。新增两份既有论文的大学对照PDF、一份作者书目HTML、获取响应与搜索记录；复用第36批L190原件扩读669–674页。**新增文献编号为0**，不把同一作品的新副本计为新论文，也不把验证页面计为取得原文。

| 材料 | 取得与实际使用范围 | 记录 |
|---|---|---|
| L189 UCSD镜像扫描 | [19页PDF](L189-crosscheck/ucsd-copy.pdf)；目视文件4／印刷395，仅复核正文θ排序、式(2)及脚注5；与旧副本同有项目方向疑点 | [范围与版本](L189-crosscheck/crosscheck-metadata.json)、[395页图像](L189-crosscheck/ucsd-pdf04-print395.png) |
| L190 Stanford镜像排印副本 | [30页PDF](L190-crosscheck/stanford-copy.pdf)；文件第1页已是663，目视文件9／印刷671的式(3)，同见负号；其他版式／全文未逐页比对 | [范围与版本](L190-crosscheck/crosscheck-metadata.json)、[671页图像](L190-crosscheck/stanford-pdf09-print671.png) |
| L190 MIT作者书目 | [原始HTML](L190-crosscheck/mit-publications.html)；只核对该篇条目的作者、1997年、112(3):663–691及JSTOR链接，不作原文或正式勘误 | 同上版本记录 |
| L190新增阅读 | 复用[原始扫描](../round-36/L190-holmstrom-tirole-1997/original.pdf)，新增文件8–13／669–674，累计663–674；未读完后续均衡 | [扩读范围](L190-extension/read-scope-extension.json)、[公式记录](../../derived/financing-followup-2026-11-12/verified-formulas.md) |
| Columbia与JSTOR响应 | DOI落地、JSTOR文章入口及PDF入口均取得HTTP200内容，但保存的是验证／挑战页面，**不是正文或勘误** | [获取记录](acquisition-attempts.json)、[分类说明](response-classification.json) |

原始获取与期刊排印／扫描的PDF都保存；正文PDF未改写。L189的页面文字提取为空，仍按扫描处理。L190 Stanford副本有文字层，但公式符号编码可能损坏，671页负号以可见图像为依据。

新扩读的6页图像、原始OCR与词框保存在[派生目录](../../derived/financing-followup-2026-11-12/README.md)，由本批范围记录连接到旧原件及其SHA256。正文OCR未逐字校订，不能称作新增6页全部文字已经可靠校订；核对过的公式与关键语义另存。

`discovery`保留检索工具回包和[查询及纳入说明](discovery/search-log.json)。初始两项查询后补做同词重复检索并归档；搜索命中不代表纳入，不下载和采用无关结果。限于本轮的关键词、作者书目与可访问入口，未取得正式勘误；不能推断正式勘误不存在。

Stanford副本初步机械定位曾误套“30页必有封面”的偏移，第10文件页实际为672；对应预览保留并准确改名，未作为671页证据。最终671页的文件页9已目视核对。这说明页数相同不能替代逐页定位。

分析、机构比较与自建模型见[本轮报告](../../../research/reviews/39-financing-open-business-argument-audit.md)。来源材料和假设模型分开，本批不提供真实用户、预算或金融效果证据。

所有本批文件的字节数与SHA256见[清单](manifest.json)，清单不包含自身。此后若补到勘误或新版本，应另存来源与差异记录，保留本轮取得范围。
