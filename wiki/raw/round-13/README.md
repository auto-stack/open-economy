# 感受 欲望与目标的机制资料

研究日期：2026年11月12日，Asia/Shanghai。对应[机制讨论](../../../research/reviews/14-needs-feelings-and-goals.md)与[阅读笔记](../../../research/reviews/14-reading-notes.md)。本批实际取得三份新增PDF，另保存一项原始PDF未取得的网络工具读取副本。

| 来源 | 实际材料 | 本轮采用范围 |
|---|---|---|
| [L63 Garfinkel等2015](L63-garfinkel-et-al-2015/metadata.json) | `web-tool-view.txt`，网络工具对10页PDF的部分文字视图；没有 `original.pdf` | 读取PDF pp.1–2概念区分，不声称已保存或读完全文 |
| [L64 Berridge与Robinson 2016](L64-berridge-robinson-2016/metadata.json) | 作者实验室10页期刊PDF及辅助文本 | pp.1–3，愉快、狭义wanting与认知性欲求；不采用临床建议 |
| [L65 Schultz等1997](L65-schultz-dayan-montague-1997/metadata.json) | 作者网站7页Science PDF及辅助文本 | pp.1–3及p.5总结；首尾含相邻文章片段，不纳入证据 |
| [L66 Desmedt等2018](L66-desmedt-et-al-2018/metadata.json) | 作者实验室5页PDF，含1页ResearchGate封面 | pp.2–4正文及p.5附录结尾；任务得分变化不等于实际能力下降同等比例 |

L64、L65、L66各有一张已渲染的相关页，分别用于核查概念表述、公式、结果与讨论。原始文件未改写，辅助文本不替代排版页。详细期刊页码、版本、方法及局限见阅读笔记。

## 失败获取与工具副本

L63首次镜像请求超时。Sussex旧网址转向Figshare后返回403，公开仓储API也返回403；对应尝试和响应保留，API响应不是合法JSON时使用txt保存。网络工具能够读取最初PDF的部分文字，因此将返回内容原样另存为 `web-tool-view.txt`，不冒充原始PDF。该视图还包含仓储网页403的工具结果，具体读取范围写入元数据。

部分原文可在网络工具中读到而不能从本机取得，两个状态分别记录。本批原始PDF下载成功数量为三，不将L63计入。

## 复用与检索

L55 Deci与Ryan 2000沿用[第十一批原文](../round-11/README.md)，本轮完整重读PDF pp.10–12，并在 `reused-sources.json` 记下路径和SHA-256。既有L54、L61、Q2、Q5用于保持概念口径，不重复计为新增阅读。

四份 `search-*.json` 保存检索返回，`L63.../web-tool-view.txt` 保存后续打开记录；搜索中出现但未采用的材料不算已读来源。本轮是定向机制阅读，不是较新研究的完整更新或系统综述。

[manifest.json](manifest.json)分别列出三份PDF、一份工具读取副本及本批辅助文件的字节数与SHA-256，清单自身与缓存不计入。版权与许可声明保留，本地研究存档不授予公开再分发许可。未来AutoDown导入时，应保留原文、工具副本和获取失败三者的状态区别。
