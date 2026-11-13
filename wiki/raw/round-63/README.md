# 第63批　合作在同一任务中改变了什么

2026年11月13日。第三部分第1章采用五项原始研究。不同稿本、三个子实验、同一数据集的多张表均按其归属标识。[增订综述](../../../research/surveys/03-competition-cooperation-distribution/competition-cooperation-and-order.md#6-同一任务中的个人汇总与配合) · [书章](../../../book/part-03/01-cooperation-and-common-capabilities.md) · [论证卡](../../../book/argument-cards/part-03-01-cooperation-and-common-capabilities.md) · [来源元数据](metadata.json) · [下载记录](download-log.json) · [文件校验](manifest.json)

| 来源与读取范围 | 实际保存的版本与依据 | 采用与限制 |
|---|---|---|
| L267 Barragan-Jason等，2021，学校儿童拉绳。图1、方法及首试结果 | [HAL作者稿](L267-rope/author.pdf) · [按页文字](L267-rope/author.txt) · [2020年预印本](L267-rope/preprint.pdf) · [期刊](https://doi.org/10.1098/rspb.2020.2951) | 核对作者稿PDF第5–8页及期刊方法中绳端的距离、单边拉动、先松手、最多三次尝试和结束后发放奖励。145对儿童中91对首试共同成功。装置条件和实际双人表现分别取证。论文所列Dryad接口本次仅返回[不可查看状态](L267-rope/dryad.json)，本地没有逐人或逐试数据，未复算回归。 |
| L268 Barrera-Lemarchand等，2026，*Collective problem decomposition improves the wisdom of deliberative crowds* | [发表版全文XML](L268-deliberation/article.xml) · [可检索正文](L268-deliberation/article.txt) · [作者数据目录](L268-deliberation/osf-files.json) · [图1分析脚本](L268-deliberation/osf/figure_1.m) · [作者项目](https://osf.io/bru7k/) · [期刊](https://doi.org/10.1038/s41467-026-76365-y) | 研究1图1C、研究2图4、研究3图6及相应方法。另存三项实验的公开个人表、组表与图1、4、6代码。本书复核研究1，研究2、3据原文，不声称复算回归、随机化推断或谈话编码。 |
| L269 Toma与Butera，2009，*Hidden Profiles and Concealed Information* | [洛桑大学存档的排印稿](L269-hidden-profiles/article.pdf) · [按页文字](L269-hidden-profiles/article.txt) · [期刊](https://doi.org/10.1177/0146167209333176) | PDF第5–8页，实验1。两种指令、讨论停止条件、录像编码及两种正确率。相对讨论内容的线索份额与图1按可用量计算的指标不同。未取得逐组转录重新编码。 |
| L270 Ring、Kavussanu与Cooke，2022，*Effects of Cooperation and Competition on Performance, Emotion, and Effort* | [班戈大学存档稿](L270-basketball/article.pdf) · [按页文字](L270-basketball/article.txt) · [期刊](https://doi.org/10.1123/jsep.2020-0357) | PDF第10–16页及第32页表1。每人每次三分钟的累计质量分、出手数和实际进球分开计。个人总是先测。作者稿表1右边缘部分未完整显示，正文第15–16页可核对比较方向，四个主要均值在表中均可读。 |
| L271 Minson、Mueller与Larrick，2017年在线、2018年卷期，*The Contingent Wisdom of Dyads* | [作者网站的期刊在线优先版](L271-dyads/article.pdf) · [按页文字](L271-dyads/article.txt) · [期刊](https://doi.org/10.1287/mnsc.2017.2823) | PDF第8–13页，尤其研究2方法、表2及关于讨论时机的结果。题目边界与先独答、先讨论的比较。基准随设计取自组内或另一条件。采用作者结果，未复算个人数据。 |

### 可重复的同题比较

[研究1个人表](L268-deliberation/osf/data_experiment_1__by_participant.csv)与[同组同题的联合答案表](L268-deliberation/osf/data_experiment_1__with_features.csv)可按组号、题号连接。先按作者图1代码处理第三题的量级、排除指定组，并按题目用初值中位数及绝对中位差筛选，得到325个组题。图1C先在组内平均，再按125组等权。再单列能找齐四人初值且与作者初始均值一致的294个组题，分别比较联合答案与四人平均、与知道真值后选出的最佳初答。后一步是本书的描述性检验，重复出场的组或题不作为独立样本计算显著性。[复核程序](../../../research/surveys/03-competition-cooperation-distribution/check-deliberation-estimates.py) · [筛选、计数及阶梯实例](crosscheck-metadata.json)

第55批的[双人辨别与双人定位原件](../round-55/README.md)和第33批的[最低努力协调博弈](../round-33/README.md)继续沿用原编号。五项新增研究没有直接检验企业的长期维护、分配正当性或Open Business的必要性。
