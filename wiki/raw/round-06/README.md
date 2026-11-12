# 第六批归档 Q5 记忆预测与复用

获取日期：2026年11月11日。四项新增原文已取得 PDF；软件复用综述线索的获取失败另行记录，未作为纳入全文。研究用途见[阅读笔记](../../../research/reviews/06-reading-notes.md)，结论见[Q5 专题](../../../research/reviews/06-memory-prediction-reuse.md)。

| 编号 | 来源 | 本地正文 | 实际版本及重点 |
|---|---|---|---|
| L28 | Kelly，1956 | [PDF](L28-kelly-1956/original.pdf) | BSTJ 35(4):917–926 的课程重印副本；定向核查 pp.917–922 |
| L29 | Bialek、Nemenman、Tishby，2001 | [PDF](L29-bialek-et-al-2001/original.pdf) | Neural Computation 13:2409–2463 大学副本；PDF pp.8–9、13 |
| L30 | Rivoire、Leibler | [PDF](L30-rivoire-leibler-2011/original.pdf) | arXiv 1010.5092v1，索引提交日期 2010-10-25，期刊文章发表于 2011；PDF 另印 2018-10-25，分别记录 |
| L31 | Still、Sivak、Bell、Crooks，2012 | [PDF](L31-still-et-al-2012/original.pdf) | arXiv 1203.3271v3，2012-10-05；重点 PDF pp.1–4 |

每项采用来源的 `metadata.json` 保存下载地址、获取时间、版本、文件 SHA-256 与实际读取范围。`extracted.txt` 是检索辅助，不替代公式和原始排版；`read-p*.png` 为阅读渲染。`manifest.json` 汇总本批文件校验值，不包含它自身。

## 获取失败与未纳入材料

`L32-krueger-1992` 保留 *Software Reuse* 的获取尝试：MIT 地址连接超时、系统原生请求超时，另一大学旧路径返回 404，出版方地址返回 403。未将这些响应或搜索摘要算作原文。

`L33-reuse-survey-candidate` 保留 NYU 的 *Software Reuse: Survey and Research Directions* 线索；请求读取超时。该编号仅保留为后续检索线索，没有确认稿件版本及读取正文。本轮涉及复用的已有工程依据为前批 L23，其余为本项目明确声明的模型假设与计算。

本轮没有关闭证书验证或把失败页标记为已下载全文。获取失败不影响前四项正文的阅读，但软件复用综述与现实成本研究仍需后续补充。

## 检索记录与复用

`search-01.json` 至 `search-05.json` 保留定向检索返回；`discovery-01.json` 核对 arXiv 版本与出版记录，`discovery-02.json` 保留复用材料的进一步查找结果。记录中有些含查询与完整结果对象，有些是完整工具文本，保留时不改写为摘要。

已保存的 L02、L20、L23 仅引用既有档案，没有再下载重复副本。其他检索命中只作发现线索，未取得正文或未阅读的观点不计入本轮证据。全周期复用、顺序检索及共享错误模型另存于 `research/examples`。

原文保留版权和许可信息，书目年份、提交年份与下载文件的排印日期分开记录，供未来 AutoDown 转换复核。
