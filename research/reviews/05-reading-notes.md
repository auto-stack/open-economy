# Q4 模块与接口的定向阅读

日期：2026年11月11日。范围：模块的不同含义、形成机制、接口成本与层级解释。新增五项正文，复核既有 Simon 文献；计算例子为本项目另建模型。

本轮以模块如何减少依赖、何种选择压力促成模块、怎样计算接口负担为纳入问题。采用原作者论文、大学副本与研究机构公开稿；检索返回和下载状态见[第五批归档](../../wiki/raw/round-05/README.md)。这是定向阅读，未覆盖全部模块性演化、网络动力学或组织设计研究。

## L23 信息隐藏与设计依赖

David L. Parnas，1972，*On the Criteria To Be Used in Decomposing Systems into Modules*，Communications of the ACM 15(12)，1053–1058。[DOI](https://doi.org/10.1145/361598.361623)；[Tufts 大学存档](https://www.cs.tufts.edu/comp/150FP/archive/david-parnas/criteria.pdf)；[本地正文](../../wiki/raw/round-05/L23-parnas-1972/original.pdf)。原 Maryland 地址返回 403，采用另一大学公开副本。

实际核查全文六页，重点 pp. 1054–1058 的 KWIC 划分、变更依赖、实现效率及结论。模块在这里是设计责任的分配，未必对应一段连续执行流程或一个子程序。作者比较按流程划分与围绕可能变化的设计决策进行封装：只要接口维持相应约定，某些内部变化就不需要调用者共同修改。

原文也讨论频繁过程调用的效率负担，以及设计上的模块边界不必原样成为运行时边界。p. 1058 明确将层级结构与良好的分解作为不同性质。对本项目而言，这提供了“减少变更依赖”的具体机制，不能推广为每次拆分都会减少运行成本。

这里的信息隐藏是避免其他模块依赖内部设计，并不以源代码保密或排他所有权为定义条件。开放实现与保留抽象接口可以并存，这是把该概念用于开放协作时需要保留的区分。

## L24 生物功能模块与连接

Leland H. Hartwell、John J. Hopfield、Stanislas Leibler、Andrew W. Murray，1999，*From Molecular to Modular Cell Biology*，Nature 402 Supplement，C47–C52。[DOI](https://doi.org/10.1038/35011540)；[Princeton 大学副本](https://www.cs.princeton.edu/~chazelle/courses/BIB/Hartwell.pdf)；[本地正文](../../wiki/raw/round-05/L24-hartwell-et-al-1999/original.pdf)。

核查 C47–C51 / PDF pp. 1–5，重点 C48 的功能模块定义与隔离、连接及组分复用。作者提出功能模块可由空间定位或相互作用的化学特异性实现，不要求每个模块都有一层物理外壳。组分也可能在不同时刻参与不同模块。

隔离减少串扰，连接支持功能整合；两者需要结合研究。作者用体外重构、移植及模型与实验相互约束讨论模块识别。这篇是概念与研究方向文章，不能把其中所有例子当成本项目独立核查的实验结果，也不能据此断言细胞全部功能都能分割成互不重叠的盒子。

## L25 共享子问题与目标变化

Nadav Kashtan、Uri Alon，2005，*Spontaneous Evolution of Modularity and Network Motifs*，PNAS 102(39)，13773–13778。[DOI](https://doi.org/10.1073/pnas.0503610102)；[作者保存的正文](https://www.nadavkashtan.com/_files/ugd/e65e7b_c9693c86ffca448f985f89dc0e604a0f.pdf)；[本地正文](../../wiki/raw/round-05/L25-kashtan-alon-2005/original-author.pdf)。作者索引将末页写成 13779，实际 PDF 末页为 13778，按正文记录。

核查 Methods、Results 与讨论，PDF pp. 1–4、6。文中演化电路与神经网络；重要条件是目标交替时保留部分共享子问题。随机更换无共同子问题的目标，在所报告实验中并未产生同样的模块结构。固定目标下，即使任务可分解，演化解也可能非模块化；已有模块还可能在器件数量压力下被破坏。

这为一种形成机制提供计算证据，不能改写成“一切环境变化都会产生模块”。网络编码、突变、选择、变化频率和任务集合均属于机制条件。本轮未重跑原文演化或其补充材料。

## L26 连接成本的选择压力

Jeff Clune、Jean-Baptiste Mouret、Hod Lipson，2013，*The Evolutionary Origins of Modularity*，Proceedings of the Royal Society B 280，20122863。[DOI](https://doi.org/10.1098/rspb.2012.2863)；[作者副本](https://jeffclune.com/publications/2013-CluneEtAl-EvolutionaryOriginsModularity-RoyalSociety.pdf)；[本地正文与附带补充材料](../../wiki/raw/round-05/L26-clune-et-al-2013/original.pdf)。文件共 23 页，包括出版封面、9 页期刊正文及补充材料。

实际核查期刊 pp. 1–7 / PDF pp. 2–8 的实验设计、结果、讨论及网络与选择算法；补充材料保留，未逐项复现。作者比较仅选择任务表现与同时考虑连接成本的计算演化。主要实验每处理 50 次，运行 25,000 代；成本涉及连接几何长度的平方和，也检查按连接数计算的替代形式。

结果支持连接成本在所研究模型中促成模块性，包括环境不变时；功能是否对应任务分解仍需另外测量。作者也明确承认形成机制可能不止一种。适应快可能是某种结构的后果，不能仅凭该后果就认定它是结构最初形成的原因。

作者网站的新闻介绍比论文中的条件更宽。本轮采用正文与方法，不把“解决了生物模块性起源”等宣传性表达作为结论。对自然系统中成本、遗传变异与选择过程的映射需要独立证据。

## L27 技术边界与交易位置的早期模型

Carliss Y. Baldwin、Kim B. Clark，2002，*Where Do Transactions Come From? A Perspective from Engineering Design*，2002-09-26 讨论稿。[NBER 会议公开稿](https://users.nber.org/~confer/2002/orgec02/baldwin.pdf)；[本地正文](../../wiki/raw/round-05/L27-baldwin-2002/original.pdf)。

核查稿件 pp. 1–2、10–12、19–24。论文将生产描述为任务与转移网络，区分一般转移与按其定义需要标准化、计量和补偿的交易，并解释为何某些边界更容易承担交易接口。稿中讨论在局部复杂协作中保留不逐项结算的空间。

这里只作为经济连接的早期理论线索。实际取得的是两位作者的 2002 年草稿，不能按 Baldwin 独著、2008 年期刊文章引用，也不能假定两版本论证相同；2006 年 HBS 文件未能取得。草稿封面和版权信息按原样保留，笔记采用概述而非逐字摘录。

这个框架已经引入参与者、知识限制、标准化、计量及支付，属于新增经济假设。技术上有接口，并不意味着该处必须设价格、必须成立企业或必须开放准入。

## 复核 L02 与既有网络证据

[Simon，1962](../../wiki/raw/round-01/L02-simon-1962/original.pdf)，*The Architecture of Complexity*。本轮重读 pp. 470–471 的装配中间体及 pp. 474–475 的近可分解性，PDF pp. 5–6、9–10。稳定中间成果缩小中断损失范围；内部快、外部慢的动态结构支持不同时间尺度的描述。两种机制相关但不能互相替代。

Simon 使用的广义层级是部分组成更大整体的嵌套结构，不能直接解释为社会中的上下级权威。其近可分解描述也要求相应耦合与时间尺度，不能只凭画出树状图就认定成立。本轮的装配模型与四节点模型受这些问题启发，参数和方程另行给出，不复述原文估算为本项目计算结果。

既有 [L10、L12](02-reading-notes.md)关于社区识别与模块度分辨率的结果继续有效：网络指标产生候选划分，功能、接口和边界理由需要各自证据。本轮没有再次下载这些已归档文件，也没有据密集社区直接识别独立经营者。

## 覆盖边界

本轮建立了从动力学、设计依赖和计算演化到经济接口的研究地图。故障维修、带时延的控制、不对称网络、重叠模块识别、治理与现实行业资料仍需后续专题。现有结果支持带条件的机制研究，尚未建立模块数、层级深度与经济效率的通用比例关系。
