# 第五批归档 Q4 模块接口与层级

获取日期：2026年11月11日。新增五项可核查 PDF，复用已在第一、二批归档的 Simon 和网络方法文献。实际阅读范围见[阅读笔记](../../../research/reviews/05-reading-notes.md)，研究判断见[Q4 结论](../../../research/reviews/05-modules-interfaces-hierarchy.md)。

| 编号 | 来源 | 保存的原文 | 版本 |
|---|---|---|---|
| L23 | Parnas，1972 | [PDF](L23-parnas-1972/original.pdf) | Tufts 大学保存的 CACM 15(12):1053–1058 副本 |
| L24 | Hartwell 等，1999 | [PDF](L24-hartwell-et-al-1999/original.pdf) | Princeton 大学保存的 Nature 402 Supplement:C47–C52 副本 |
| L25 | Kashtan、Alon，2005 | [PDF](L25-kashtan-alon-2005/original-author.pdf) | 作者资料库的 PNAS 102(39):13773–13778 副本 |
| L26 | Clune、Mouret、Lipson，2013 | [PDF](L26-clune-et-al-2013/original.pdf) | 作者存档，含出版封面、期刊正文与补充材料，共 23 页 |
| L27 | Baldwin、Clark，2002 | [PDF](L27-baldwin-2002/original.pdf) | NBER 会议公开的 2002-09-26 草稿，非 2008 年期刊版本 |

各采用来源的 `metadata.json` 包含来源、版本、读取范围、获取时间、原文校验值及提取方式。`manifest.json` 汇总实际纳入的五项来源和本批文件 SHA-256；不包含自身。`extracted.txt` 是检索辅助文本，排版、公式和表格以 PDF 为准。`read-p*.png` 是核查用的渲染页。

## 获取失败与替代来源

L23 初始 Maryland 地址返回 403，保存于 `attempt-initial.json`、`response.html`；Tufts 副本成功。L25 的旧 Weizmann 路径分别出现连接重置及页面不存在响应，最终从作者网站取得有效 PDF；失败记录没有计为全文下载。

`L27-baldwin-2006` 目录仅保存 HBS 2006 文件的 403 响应和来源记录，不是第六项已取得文献。实际用于阅读的 L27 是另一个独立保留的 2002 年草稿，作者、题名和年份均按该稿记录。不能因为有同题期刊文章，就将草稿默认为期刊全文。

本轮没有取得并引用二手摘要来替代上述五项正文。仅作发现线索的其他检索命中没有逐项下载；检索返回、出版索引和失败情况保存在本批 JSON 中。

## 检索记录

`search-01.json` 至 `search-05.json` 保留分组检索返回，`discovery-01.json` 至 `discovery-04.json` 保留打开作者目录、追踪 PDF 和失效地址的结果。其中有的记录为包含查询与结果的对象，有的为工具完整文本返回；均保留获取时的内容，不用后来摘要覆盖。

纳入方向为设计分解、生物功能模块、模块形成的计算演化和交易边界的理论线索。初始也检索了生物模块性综述，但未据检索片段纳入其观点。采用的是定向选读方案，不表示系统覆盖所有学科的模块性研究。

原始文件保留版权、许可和稿件声明。研究中的两个新模型与图表位于 `research/examples`，与本批文献原文分开，未来可按 AutoDown 的导入规范转换。
