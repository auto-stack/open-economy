# Q5 记忆预测与复用的定向阅读

日期：2026年11月11日。范围：过去记录、预测信息、行动收益、物理代价与复用成本的区别。已取得的四项新增原文见[第六批归档](../../wiki/raw/round-06/README.md)，研究结论与[项目模型](06-memory-reuse-models.md)分别记录。

检索围绕 predictive information、value of information、population growth、thermodynamics of prediction、software reuse 展开。纳入正文能核查定义与条件的原始研究；没有把检索摘要当成完整证明。长篇论文仅定向阅读以下部分，本轮不构成所有预测或复用研究的系统综述。

## L28 信息与对数增长的条件性关系

John L. Kelly, Jr.，1956，*A New Interpretation of Information Rate*，Bell System Technical Journal 35(4)，917–926。[DOI](https://doi.org/10.1002/j.1538-7305.1956.tb03809.x)；[Ohio State 大学课程副本](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/Kelly1956-1uwz47o.pdf)；[本地正文](../../wiki/raw/round-06/L28-kelly-1956/original.pdf)。

核查 pp. 917–922 / PDF pp. 1–6。作者明确区分一般任务的损失函数与通信概率，并在特定下注、信息通道和增长目标中建立信息率的操作解释。二元例子已经展示：最大化财富的算术期望与最大化典型长期对数增长不是同一目标。

本项目采用这个数学连接，不将其作为现实市场的建议。原文一般推导的独立符号、噪声、赔率和允许分配条件需保留。现实组织没有因为收到消息就自动获得这种增长机制，也不能把所得对数增长率称为所有任务的收益。

## L29 过去与未来之间的统计信息

William Bialek、Ilya Nemenman、Naftali Tishby，2001，*Predictability, Complexity, and Learning*，Neural Computation 13(11)，2409–2463。[DOI](https://doi.org/10.1162/089976601753195969)；[Caltech 大学副本](https://www.its.caltech.edu/~theory/bialek_nemenman_tishby_01.pdf)；[本地正文](../../wiki/raw/round-06/L29-bialek-et-al-2001/original.pdf)。

定向核查 §3 的预测信息定义、平稳过程表达及 Markov 例子，印刷 pp. 2416–2417、2421 / PDF pp. 8–9、13。这里预测信息是过去与未来随机变量之间的互信息。平稳性支持把窗口长度与块熵联系起来；对 Markov 过程，过去与未来的相互信息可以归结到边界状态。

这提供了“记录很多”与“对未来有信息”的区别。它既不等同于实际预测器已经学会该分布，也不保证某个任务更有收益。本轮没有复现有限参数与非参数学习的全部渐近推导，不采用论文的复杂性唯一性讨论作为本项目的新公设。

## L30 群体结构与信息价值

Olivier Rivoire、Stanislas Leibler，*The Value of Information for Populations in Varying Environments*。期刊为 Journal of Statistical Physics 142，1124–1166，2011，[DOI](https://doi.org/10.1007/s10955-011-0166-2)。实际阅读 [arXiv 1010.5092v1](https://arxiv.org/abs/1010.5092v1) 的[本地 PDF](../../wiki/raw/round-06/L30-rivoire-leibler-2011/original.pdf)。

arXiv 索引记录首次提交为 2010-10-25，只有 v1；下载 PDF 首页另印 2018-10-25。这三个日期分别保存，不将首页排印日期当成期刊出版或已确认的修订日期，也不按期刊页码定位预印本。

实际核查预印本 p. 5 的模型假设、§IV pp. 10–12、§V–VI pp. 12–15，以及 p. 20 的实施成本问题。三个简化条件尤其重要：不继承上代信息、线索由群体共同获得、只有与环境相匹配的类型能够繁殖。在相应情形，最优增长增益与互信息联系，错误分配带来的损失与 KL 散度联系。

作者逐项放松假设：加入遗传信息和时间因果约束后，增量信息的表达会改变；个体分别获得随机线索时，群体的信息收益也不能简单拿单个成员的互信息上界替代。计算群体长期增长、单个主体期望收益及成员间共同风险，是不同问题。

原文 p. 20 明确把策略的实施成本列为尚未完整解决的问题。项目的验证、维护与更新成本是另建模型中的假设，不冒称从该文增长公式中自动得到。

## L31 预测与耗散的物理联系

Susanne Still、David A. Sivak、Anthony J. Bell、Gavin E. Crooks，2012，*The Thermodynamics of Prediction*，Physical Review Letters 109，120604。[DOI](https://doi.org/10.1103/PhysRevLett.109.120604)；[arXiv 1203.3271v3](https://arxiv.org/abs/1203.3271v3)；[本地 PDF](../../wiki/raw/round-06/L31-still-et-al-2012/original.pdf)。版本为 2012-10-05，五页。

核查 PDF pp. 1–4 的物理设定、式 (11)–(18) 与讨论。系统与热浴接触，响应无系统反馈的随机外部驱动；状态按指定 Markov 转移响应，驱动改变与系统弛豫分步处理。原文采用自然对数，信息单位为 nat。

作者将关于当前驱动的瞬时互信息与关于下一驱动的预测互信息相比较，得到驱动改变步骤的功耗散关系，并对整个过程给出包含弛豫贡献的下界。分步的等式与完整过程的下界不能互换；其瞬时信息量也不等于 L29 的整段过去与整段未来的互信息。

该框架中的隐式预测指系统状态与未来驱动之间的统计关系，不要求系统具有可自述的世界模型。论文不是“一切记忆保存每秒有固定耗电”的证明，也没有推导任何组织达到复杂度阈值就必然进化出显式内部模拟器。对系统能够反过来改变环境的组织，需要重新检查物理与因果条件。

## 复核既有复用线索

[L23 Parnas](05-reading-notes.md#l23-信息隐藏与设计依赖)，特别是 pp. 1056–1058：设计责任、调用关系与可保留的底层能力为修改及复用提供条件，但接口、实现开销和依赖约束需要另外说明。本轮据此保留“可用成果不等于免费可复用成果”的问题，而没有把旧工程讨论当作当代软件行业的经验统计。

[L02 Simon](01-reading-notes.md#l02)：Q4 的稳定中间成果机制在本轮增加任务间的失效、检查及更新假设。跨任务复用与一次任务内部的装配检查点不同，二者只共享需要稳定保存这一条件。

[L20 Kolchinsky、Wolpert](04-reading-notes.md)：本轮不新增其文献结论；仍保留通过改变信息关系检验维持贡献的思路。成本比较没有代替因果干预，预测准确也不自动等于自主性。

## 尚待补充的材料

软件复用的完整专题综述、非平稳学习、主动感知、带反馈的控制和认知模型的经验研究尚需补充。本轮对 Krueger 1992 及 NYU 复用综述线索的正文获取情况按归档记录处理；未取得并核查的材料不作为上述结果的依据。

本轮的全周期复用与共享错误例子均为项目构造的有限模型；它们承担逻辑比较的用途，不能替代工程投入、真实失效率或组织行为的测量。
