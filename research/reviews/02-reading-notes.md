# 组织识别判据的补充阅读

日期：2026年11月11日。范围：补充第一轮尚未明确的“集合与有组织系统怎样区分”，重点阅读性质对关系的依赖、因果证据和边界识别方法。新增四项来源，均保存原始 PDF，属于定向阅读，不是系统综述。

原始资料、检索记录与版本信息见[第二轮归档](../../wiki/raw/round-02/README.md)。沿用第一轮的 L02、L04、L06 等编号，新来源接续为 L09 至 L12。

## 检索与筛选

三批检索分别保存于归档目录的 `search-01.json`、`search-02.json`、`search-03.json`。完整检索式如下：

1. `Wimsatt aggregativity emergence four conditions permutation intersubstitution pdf`；`Newman Girvan 2004 finding evaluating community structure networks pdf modularity`；`Pearl causal inference statistics overview 2009 pdf intervention confounding`。
2. `"Wimsatt" "Emergence as Non-Aggregativity" filetype:pdf`；`"Wimsatt" "Aggregate" "four" site:philsci-archive.pitt.edu`。
3. `"10.1007/s11229-006-9017-0"`；`"Resolution limit in community detection" Fortunato Barthelemy 2007 pdf`。

最初尝试获取 Wimsatt 的回顾性章节未取得 PDF，改读大学存档中的另一篇原作者论文 L09。它不是该章节或 2000 年论文的替代版本，引用必须按实际题名与年份。Wimsatt 2000 年论文、书评和其他二手评论本轮只作检索线索，不据其摘要或片段建立结论。

L10 的大学链接证书校验失败，改存 arXiv 原作者预印本。L12 针对“用网络指标识别组织边界”的局限补入，防止只收集支持指标有效性的材料。网络检索未按数据库与年份穷尽覆盖。

## L09

William C. Wimsatt，2006，*Reductionism and Its Heuristics: Making Methodological Reductionism Honest*，Synthese 151，445–475。DOI：[10.1007/s11229-006-9017-0](https://doi.org/10.1007/s11229-006-9017-0)。[作者所在大学存档](https://philosophy.uchicago.edu/faculty/files/wimsatt/Wimsatt-reductionism.pdf)，[本地 PDF](../../wiki/raw/round-02/L09-wimsatt/original-uchicago.pdf)。

实际核查：PDF 第 4 页关于聚合性质的讨论，第 15–17 页第 8 节关于聚合性、组织关系和分解方式的论证。该副本未显示期刊连续页码，使用 PDF 页码定位。

作者把性质是否依赖部件组织方式作为聚合性问题，强调近似、分解与适用范围。同一系统可以有不同性质，不能仅凭一种聚合性质对整体作一刀切分类。本项目据此优先提出“哪一种性质需要关系安排才能解释”的问题；这是借鉴其方法，不将非聚合性直接等同于自主组织。

## L10

M. E. J. Newman 与 M. Girvan，*Finding and Evaluating Community Structure in Networks*。期刊论文为 Physical Review E 69，026113，2004，DOI：[10.1103/PhysRevE.69.026113](https://doi.org/10.1103/PhysRevE.69.026113)。实际保存并阅读的版本为 arXiv:cond-mat/0308217v1，2003年8月11日。[原作者预印本](https://arxiv.org/abs/cond-mat/0308217)，[本地 PDF](../../wiki/raw/round-02/L10-newman-girvan-2004/original-arxiv.pdf)。

实际核查：第 I 节，PDF 第 1 页的研究对象；第 IV 节，PDF 第 7–8 页的质量比较与 modularity 定义，重点为第 8 页及公式 5。

算法即使对随机网络也能给出划分，因此作者引入与随机连接参照的比较。本轮据此把社区结构作为边界识别的证据之一，要求说明边的含义和参照模型；高模块度本身不能证明存在功能、自维持或唯一实体边界。

## L11

Judea Pearl，2009，*Causal Inference in Statistics: An Overview*，Statistics Surveys 3，96–146。DOI：[10.1214/09-SS057](https://doi.org/10.1214/09-SS057)。[大学存档](https://www.cs.columbia.edu/~blei/fogm/2018F/materials/Pearl2009a.pdf)，[本地 PDF](../../wiki/raw/round-02/L11-pearl-2009/original.pdf)。

实际核查：§2.1–2.3，印刷页 99–100，PDF 第 4–5 页；§3.2–3.2.1，印刷页 107–109，PDF 第 12–14 页。

本文区分观测关系与干预结果，并要求因果推断说明模型假设。本轮据此要求区分共同环境造成的相关性与部件之间的因果联系。现实中的连接重组会同时改变多个因素，不能仅把观测数据替换成另一张图就当作真实干预效果；证据也可以来自有明确假设的模型与自然变化，不要求破坏性实验。

## L12

Santo Fortunato 与 Marc Barthélemy，*Resolution Limit in Community Detection*。期刊记录为 PNAS 104，36–41，2007，DOI：10.1073/pnas.0605965104。实际保存并阅读 Stanford 存档的预印本：页眉标注 arXiv:physics/0607100v2，另有 February 2, 2008 的排版日期；不把它冒充期刊最终排版。[存档来源](https://snap.stanford.edu/class/cs224w-readings/fortunato06community.pdf)，[本地 PDF](../../wiki/raw/round-02/L12-fortunato-barthelemy/original.pdf)。

实际核查：第 I–II 节，PDF 第 1–2 页；第 IV–V 节，PDF 第 3–5 页的模块合并比较与环形团例子。

该研究表明，模块度优化在特定条件下可能合并本可区分的小模块，结果还受整个网络规模影响。这限制了单一指标用于识别组织边界的范围；它没有证明所有网络方法都失效。本轮据此要求边界结论说明指标、尺度与竞争划分。

## 与前一轮的关系

本轮继续使用 [L02 的近可分解性、L04 的系统变量与耦合、L06 的构成边界讨论](01-reading-notes.md)，但没有增加对这些原文其他部分的阅读声称。新增材料帮助操作化识别方法，尚不提供通用的组织程度量表。
