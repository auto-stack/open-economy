# 目标冲突 优先顺序与目标修订资料

研究日期：2026年11月12日，Asia/Shanghai。对应[研究讨论](../../../research/reviews/15-goal-conflict-and-revision.md)及[阅读记录](../../../research/reviews/15-reading-notes.md)。本轮取得三份新增论文PDF，另保存一项未取得论文全文的文献定位条目。

| 来源 | 实际材料 | 本轮读取范围 |
|---|---|---|
| [L67 Shenhav等2013](L67-shenhav-et-al-2013/metadata.json) | Princeton作者网页24页Neuron排印PDF | pp.1、3–6、17及p.18结论；EVC模型、控制组件及开放问题 |
| [L68 Shah等2002](L68-shah-et-al-2002/metadata.json) | 作者书目网页，及出版社PDF网址返回的403响应 | 只核查书目和目标屏蔽线索，未读论文实验，不纳入完成全文数量 |
| [L69 Wrosch等2003](L69-wrosch-et-al-2003/metadata.json) | CMU网站15页期刊排印PDF | pp.1–4、12–13；概念、Study 1方法、讨论与因果局限 |
| [L70 Gollwitzer与Brandstätter 1997](L70-gollwitzer-brandstaetter-1997/metadata.json) | Konstanz作者实验室14页排印PDF | pp.1–2、5–7、12；意向与计划、Study 2及灵活性问题 |

三份原文分别保存为 `original.pdf`，辅助文本为 `extracted.txt`。文字层可能包含识别错误，公式、样本分母与表格需回排版页核对；各源另有一张渲染页用于复核。下载全文不等于已读全文，本轮未逐篇完整精读。

L68的作者书目页将APA记录链接标为PDF，不能据此认定有可下载全文。另尝试的APA PDF网址返回403，响应保留为 `publisher-response.bin`，没有绕过登录或访问限制。原文未取得，不依据摘要重述其六项实验结果。

L70的实验回信子样本比例与全部招募人数分开记录；L69的三个研究是横断面关联，不能改写成目标调整改善幸福感的因果证明；L67是理论综述，不标作整个大脑功能的已定结论。

三份 `search-*.json` 保存检索结果。作者书目和出版社尝试均保留网址、HTTP状态与实际文件状态。L55与L64只沿用既有阅读，不重复计入本轮新增来源或本轮新读原文。

[manifest.json](manifest.json)记录文件字节数及SHA-256，将三份原始PDF与一项书目线索分别列出；清单本身与缓存不计入自身校验。原始版权和许可声明保留，本地研究存档不提供公开再分发许可。后续AutoDown导入时保留阅读范围、材料类型及下载失败状态。
