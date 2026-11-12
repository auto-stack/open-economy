# 第七批归档 Q6 社会经济连接

获取日期：2026年11月11日。五项新增原文已保存，版本与实际阅读范围见[阅读笔记](../../../research/reviews/07-reading-notes.md)，研究结论见[Q6 专题](../../../research/reviews/07-economic-bridge.md)。这是定向阅读，不是相关学科的完整综述。

| 编号 | 来源 | 本地原文 | 版本及实际阅读 |
|---|---|---|---|
| L34 | Samuelson，1954 | [PDF](L34-samuelson-1954/original.pdf) | REST 36(4):387–389，4页含封面；正文扫描，渲染阅读 PDF pp.2–4 |
| L35 | Hayek，1945 | [PDF](L35-hayek-1945/original.pdf) | AER 35(4):519–530，13页含封面；定向读取 pp.519–521、523–526 |
| L36 | North，1991 | [PDF](L36-north-1991/original-university.pdf) | JEP 5(1):97–112，17页含封面；正文扫描，渲染阅读 pp.97–98 |
| L37 | Ostrom，2010 | [PDF](L37-ostrom-2010/original-university.pdf) | AER 100(3):641–672；54页文件中前32页为文章，后22页是网站附加被引清单；定向读取 pp.641–642、644–647、659–661 |
| L38 | Holmström，1982 | [PDF](L38-holmstrom-1982/original.pdf) | Bell Journal 13(2):324–340，18页含封面；正文扫描，渲染阅读 pp.324–326 |

`metadata.json` 记录书目、下载地址、实际文件版本、获取时刻、SHA-256、正文和提取状态。`extracted.txt` 是检索辅助，扫描件提取结果很少，不能把封面文本当成已提取正文。`read-p*.png` 是阅读渲染；生成过图不表示该页已阅读，以 metadata 的范围为准。原始 PDF 未被改写。

`manifest.json` 汇总本批全部文件的大小与校验值，不包含自身；可用于未来 AutoDown 转换的来源复核。没有假定 AutoDown 的最终导入结构。

## 失败与版本区别

- L36 的出版方地址返回403，响应页和 `attempt-initial.json` 保留；后取得 Stanford 保存的期刊重印扫描件。
- L37 的 Nobel 演讲地址返回403，保留响应页与记录；Indiana 草稿下载连接中断，保留 `metadata-draft.json`。最终采用 Portland State 保存的2010年期刊文章，没有取得演讲或草稿 PDF，也不混用版本。
- 网页工具返回的 Indiana 草稿提取保留在 `discovery-03.json`，仅作版本发现记录，未把它列作独立采用的全文或引用其结论。实际纳入的是上述期刊 PDF。

## 检索与复用

`search-01.json` 至 `search-05.json` 保留五批定向检索返回，`discovery-01.json` 至 `discovery-04.json` 保留下载入口与版本发现过程。其他检索命中未自动纳入证据。失败页未标成论文，未关闭证书验证。

L07 Coase 和 L27 Baldwin–Clark 复用已有档案与笔记，没有重复下载。`reused-L07-p4.png`、`reused-L07-p5.png` 来自第一批原文的阅读定位渲染。本轮模型和生成图放在 `research/examples`，不冒充文献原始研究。
