# 第四批归档：Q3 熵、信息、复杂性与功能

获取日期：2026年11月11日。八项纳入来源：七份 PDF 和一份同作者同题书章 HTML。用途和实际阅读范围见[阅读记录](../../../research/reviews/04-reading-notes.md)，研究判断见[Q3 阶段结论](../../../research/reviews/04-measures-and-bridges.md)。这是一轮针对概念与条件的定向检索，不是完整系统综述。

| 编号 | 来源 | 实际保存的正文 | 版本及阅读提醒 |
|---|---|---|---|
| L15 | Shannon，1948 | [PDF](L15-shannon-1948/original.pdf) | 修正版重印，保留全文；定向阅读导论及 §6 |
| L16 | Landauer，1961 | [PDF](L16-landauer-1961/original.pdf) | 2000 年重印扫描，页码不同于 1961 原版；§3–4 视觉核查 |
| L17 | Esposito、Van den Broeck，2011 | [PDF](L17-esposito-vandenbroeck-2011/original-arxiv.pdf) | arXiv 1104.5165v2，2011-08-09；pp. 1–3 |
| L18 | Crutchfield、Young，1989 | [PDF](L18-crutchfield-young-1989/original-author.pdf) | 作者存档扫描；pp. 105–107 视觉核查 |
| L19 | Hazen 等，2007 | [HTML](L19-hazen-et-al-2007/original-chapter.html) | 国家科学院出版社同题书章，实际核查书页 25–30；未取得 PNAS PDF |
| L20 | Kolchinsky、Wolpert，2018 | [PDF](L20-kolchinsky-wolpert-2018/original.pdf) | Interface Focus 8:20180041；重点 §§3–5.1.1 |
| L21 | Tong，统计物理讲义第 1 章 | [PDF](L21-tong-statphys/original-native.pdf) | 剑桥大学讲义；未推定出版年份；重点 §1.2.1、§1.3.3 |
| L22 | Bérut 等，2012 | [PDF](L22-berut-et-al-2012/original.pdf) | Nature 483:187–189 大学副本；正文的装置与热量结果 |

## 来源与失败记录

各来源 `metadata.json` 给出最终采用文件、网址、获取时间、SHA-256、版本与阅读状态。`attempt-*.json`、其他 `metadata-*.json` 保留先前获取结果；`manifest.json` 汇总来源和本批文件校验值。manifest 不包含它自身，防止循环校验。

L17 初始机构地址超时，改用 arXiv；L18 的出版方端点返回 401，改用作者文件。L19 的旧大学地址返回 404，作者站多次连接超时，PMC 返回浏览器验证页；这些都没有算作期刊正文。`original-pmc.html` 和它最初生成的短 `extracted.txt` 仅作为验证页响应保留，实际正文提取是 `extracted-chapter.txt`。L18 的 `response.html` 实际是 JSON 错误响应，扩展名不表示内容类型。

L21 的部分获取方式遇到超时或证书校验失败，最终使用系统正常证书验证取得 PDF，没有关闭证书验证。扫描 PDF 的 `extracted.txt` 只有很少可用文字；`read-p*.png`、`reading-pages.png` 是阅读辅助渲染，原始 PDF 才是依据。

L19 原始 HTML 中部分公式和图是外部图片；两个主机下的图片链接均未返回图片内容，尝试结果见 `assets-attempt-01.json`、`assets-manifest.json`。原 HTML 保持下载字节，不替换为修改版。正文文字包含达标计数、阈值和上下文，摘要也以文字给出功能信息公式；公式图片和插图尚未完整归档，未来转成 AutoDown 知识库时需补齐，不能把这份 HTML 当作完整离线排版副本。

## 检索可追溯性

`search-01.json`、`search-02.json` 为初始检索返回；`discovery-01.json`、`discovery-02.json`、`discovery-03.json` 为寻找作者副本、核对出处等过程的返回。`search-03.json` 补充后续检索式、发现链接及结果摘要，明确区分完整返回与人工记录。仅作为检索命中、未阅读和采用的其他材料不视作纳入来源。

原始文件保留版权与许可信息。研究笔记、公式推导和本项目例子位于 `research`，没有以摘要覆盖正文；未来按 AutoDown 的实际导入规范转换。
