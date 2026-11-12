# 第八批归档 Q7 开放成果的投入与回报

获取日期：2026年11月11日。七项原文已取得，研究用途见[阅读笔记](../../../research/reviews/08-reading-notes.md)，结论见[机制比较](../../../research/reviews/08-open-funding.md)。本批是定向阅读，不是筹资、开源经济或治理的完整系统综述。

| 编号 | 来源 | 本地原文 | 实际文件和阅读范围 |
|---|---|---|---|
| L39 | Andreoni，1990 | [PDF](L39-andreoni-1990/original.pdf) | EJ 100(401):464–477；15页含封面，正文扫描；渲染阅读 pp.464–465 |
| L40 | Bagnoli、Lipman，1989 | [PDF](L40-bagnoli-lipman-1989/original.pdf) | REStud 56(4):583–601；20页含封面；定向读取 pp.583–587 |
| L41 | Tabarrok，1998 | [PDF](L41-tabarrok-1998/original.pdf) | Public Choice 96:345–362；定向读取 pp.345–350 |
| L42 | von Hippel、von Krogh，2002稿 | [PDF](L42-vonhippel-vonkrogh-2002/original.pdf) | 2002-04-30工作稿，标示拟于2003年发表，31页；读取封面及 pp.16–18 |
| L43 | Riehle，2012对应作者稿 | [PDF](L43-riehle-2012/original.pdf) | 13页作者排版稿，地址路径为2010年；读取 p.1、pp.3–6；2012年期刊书目另据作者页面 |
| L44 | Conti 等，2023年11月稿 | [PDF](L44-conti-et-al-2023/original.pdf) | NBER WP31668，49页，封面修订日期2023年11月；读取 PDF pp.1–6、10–11、13–17、26–27 |
| L45 | Zhang 等，2022 | [PDF](L45-zhang-et-al-2022/original.pdf) | CHI ’22作者副本，18页；定向读取 pp.1–3、5、7、9–10、15–16 |

原始 PDF 保留下载内容及版权声明。`metadata.json` 记录作者、题名、书目、实际版本、获取时刻、地址、大小、SHA-256及实际阅读范围。`extracted.txt` 仅作检索辅助；L39正文扫描，提取结果几乎不含正文，使用阅读渲染核对。生成过的 `read-p*.png` 不自动表示该页已读，以 metadata 范围为准。

`manifest.json` 包括本批文件大小与 SHA-256，不包括自身。原文、书目页面、失败响应、检索记录和提取文本分别保留，供后续 AutoDown 转换。没有推定原文可重新分发或已确定 AutoDown 导入结构。

## 版本和获取记录

- L42 的 MIT 旧路径返回404，响应保存为 `response.html`，原尝试保存为 `attempt-initial.json`。随后取得作者网站工作稿。未把工作稿标成期刊出版版。
- L43 保存作者书目页面原始 HTML、提取文本和下载 metadata。作者页将书目更新为2012年期刊文章，实际 PDF 为作者稿；没有用网址中的2010替代书目年份，也没有伪造期刊排版页码。
- L44 保存 NBER 书目页面 HTML、提取文本及 metadata。页面写修订于2024年8月，实际取得的 PDF 封面写修订于2023年11月；采用和引用后者。目录因此用2023，不把网页日期当作已取得的新版文件。正文样本数的不同表述在阅读笔记中保留，未据其计算覆盖率。
- 网页工具访问 NBER 书目页曾返回403，保存在 `discovery-01.json`；本地常规请求随后成功，原始 HTML 已存。网页工具失败不表示 PDF 获取失败。

## 检索与复用

`search-01.json` 至 `search-03.json` 保留本轮定向检索结果；第三批同时含 Riehle 作者页面的发现记录。`discovery-01.json` 保留书目入口核查。没有把检索摘要当作正文。Bergstrom–Blume–Varian、Lerner–Tirole 和其他未纳入命中不算已读来源。

Q6 的公共品、制度和激励资料复用既有档案，不重复下载。本轮合同、服务净额与多期预算模型是项目自建说明，保存在 `research/examples`，不放进原始文献目录。
