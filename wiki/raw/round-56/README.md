# 第56批　双人定位试次配对与固定规则比较

2026年11月13日。本批复用L240同一篇论文的实验方法与作者补充表S2。原件保留在第55批，来源编号沿用L240。本批收录本项目计算所得的逐行对照与结果。[作者工作簿](../round-55/L240-wisdom-dyads/mmc2.xlsx) · [原文全文](../round-55/L240-wisdom-dyads/article.jats.xml) · [所用原件与校验值](source-reuse.json)

- [逐条配对清单](trial-pairing.tsv)覆盖四张实验表的全部2,560条联合记录。`joint_row`、`solo1_row`、`solo2_row`是同一张原表含表头的行号。两位成员各自最近的合格独立记录都列出；`valid=1`表示联合试次筛选通过。目标坐标单位为原坐标的百分之一，每格1.28毫米。对两列平方距离取较大值，小于等于0、1、25或100即可重建精确、1.28、6.4或12.8毫米的覆盖清单。
- [比较结果](comparison-results.json)按实验记录总数、排除状态、独立同目标行对、半径子集和逐块均值。`distributional`为跨目标的模型基准，`nearest`为近邻结果，`diff_mean`为真实误差减规则误差。各有16对独立搭档，四表分开计算。
- [预定规则](../../../research/surveys/01-organization-maintenance/relational-organization-and-boundaries/dyad-comparison-protocol.md)、[复算程序](../../../research/surveys/01-organization-maintenance/relational-organization-and-boundaries/compare_dyads.py)及[研究报告](../../../research/surveys/01-organization-maintenance/relational-organization-and-boundaries/dyad-trial-comparison.md)说明可识别范围。从任意目录运行该程序（Python 3及openpyxl）会由第55批原件重建本批两份计算结果。[批次元数据](metadata.json) · [文件校验清单](manifest.json)
