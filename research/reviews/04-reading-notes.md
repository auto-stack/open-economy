# Q3：熵、信息、复杂性与功能的定向阅读

日期：2026年11月11日。状态：完成本轮定向阅读，供讨论；不是系统综述，也没有证明通用组织理论已经成立。

本轮围绕旧讨论的 C01、C14 及 KL 散度版 Ordo，选择八项来源。检索覆盖 Shannon entropy、Landauer erasure、nonequilibrium free energy / relative entropy、statistical complexity、functional information 和 semantic information。优先使用原始论文、作者存档和大学课程原稿，纳入标准是正文能够核查定义、条件或具体证据。没有用搜索摘要补足未取得的正文。

原文、提取文字、获取失败及检索记录见[第四批归档](../../wiki/raw/round-04/README.md)。L19 最终取得同作者同题的国家科学院出版社书章，未取得期刊 PDF；不能按期刊页码引用书章。扫描的 L16、L18 依据渲染页阅读，文字层不能代替原件。以下为定向核查范围，没有声称读完全部证明、附录和实验数据。

## L15：通信信息的定义

Claude E. Shannon，1948，*A Mathematical Theory of Communication*，Bell System Technical Journal 27，379–423、623–656。[耶鲁大学保存的修正版重印](https://www.cs.yale.edu/homes/yry/readings/general/shannon1948.pdf)；[本地原文](../../wiki/raw/round-04/L15-shannon-1948/original.pdf)。

核查 introduction 和 §6，PDF pp. 1、10–12。作者研究消息选择的不确定性及传递问题，主动限定了工程问题与语义问题的关系；这不是声称信息在其他研究中不可能具有意义。

H 的形式与选定概率分布有关；联合熵通常不能按各部分熵直接相加。条件熵刻画获得一个变量后另一个变量剩余的不确定性。对本项目的作用：必须说明“关于什么的信息”，不能把消息本身的熵、对环境的相关信息和行动收益当成一个量。

## L16：原始 Landauer 论证

Rolf Landauer，1961，*Irreversibility and Heat Generation in the Computing Process*，IBM Journal of Research and Development 5，183–191。[DOI](https://doi.org/10.1147/rd.53.0183)；[大学存档](https://www.cpt.univ-mrs.fr/~verga/pdfs/Landauer-1961uq.pdf)；[本地原文](../../wiki/raw/round-04/L16-landauer-1961/original.pdf)。实际文件是 2000 年重印，重印页码 261–269。

核查 §3–4，PDF pp. 4–5 / 重印 pp. 264–265。原文明确讨论对称二态物理存储器的标准复位，从两态等概率到确定态，熵减少 k_B ln 2，由环境补偿。作者也区分输入已确定、偏置或有关联等情况。相关页还明确容许存储信息而不耗散的理想化描述。

因此不能从该结果推出“保存一个 bit 每秒至少消耗固定能量”。原文对可逆计算用途的历史判断，也不作为今天一切计算必须采用某种实现的定理。本轮采用的仅是明确复位条件下的论证，并结合 L17、L22 检查现代形式与实验范围。

## L17：相对熵与非平衡自由能

Massimiliano Esposito、Christian Van den Broeck，2011，*Second Law and Landauer Principle Far from Equilibrium*，EPL 95，40004。[DOI](https://doi.org/10.1209/0295-5075/95/40004)；[arXiv 1104.5165v2](https://arxiv.org/abs/1104.5165v2)；[本地预印本](../../wiki/raw/round-04/L17-esposito-vandenbroeck-2011/original-arxiv.pdf)。实际文件版本标为 2011-08-09。

核查预印本 pp. 1–3，尤其式 (3)–(15)。在文中系统、热浴和理想功源的描述下，定义非平衡自由能，并建立它与对应正则平衡分布的相对熵之间的等式。本文省略的 k_B 在本项目公式中恢复；KL 使用自然对数。

这是信息论与热力学的实质联系，不只是形式类比。其条件包括概率所描述的物理状态、能量函数及参考热浴。可提取功的上限与达到该上限的实际可控性分开；原文也指出理论控制步骤可能不具备实际可操作性。没有由此定义任意社会网络的功能、价值或智能。

## L18：随机性与预测结构

James P. Crutchfield、Karl Young，1989，*Inferring Statistical Complexity*，Physical Review Letters 63，105–108。[DOI](https://doi.org/10.1103/PhysRevLett.63.105)；[作者存档](https://csc.ucdavis.edu/~cmg/papers/ISC.pdf)；[本地扫描](../../wiki/raw/round-04/L18-crutchfield-young-1989/original-author.pdf)。

实际视觉核查 pp. 105–107，PDF pp. 1–3。作者从测量符号序列重建 ε-machine，区分动力学熵与描述预测结构所需的状态信息。p. 107 的 α=1 情况使用预测机器稳态顶点分布的 Shannon 熵。

这为“随机性大”与“预测组织复杂”提供不同刻画。本项目只用可直接分析的恒定、交替和独立抛币过程说明区别，未复现文中的 logistic map 重建算法。具体复杂性依赖观测、尺度与预测建模；它不是全部图结构复杂性、计算难度和组织任务能力的共同单位。

## L19：指定功能下的配置稀缺性

Robert M. Hazen、Patrick L. Griffin、James M. Carothers、Jack W. Szostak，2007，*Functional Information and the Emergence of Biocomplexity*。期刊条目 PNAS 104 Suppl. 1，8574–8581，[DOI](https://doi.org/10.1073/pnas.0701744104)。

实际阅读[国家科学院出版社同题书章](https://uwnxt.nationalacademies.org/read/11790/chapter/5)，载 *In the Light of Evolution: Volume I: Adaptation and Complex Design*，[书籍 DOI](https://doi.org/10.17226/11790)；[本地 HTML](../../wiki/raw/round-04/L19-hazen-et-al-2007/original-chapter.html)。核查书页 25–30，特别是 pp. 29–30 的定义；未复现 Avida 或 RNA 研究。

功能信息按达到指定功能阈值的配置比例计算，需要先给出配置空间、功能和阈值。正文使用达到或超过阈值；摘要使用的大于号不代替正文定义。它衡量这一参照下的达标稀缺性，不等于当前样本群体的 Shannon 熵。作者将没有任何可行配置的情况记为未定义，不能称作无限能力。

## L20：信息的因果贡献

Artemy Kolchinsky、David H. Wolpert，2018，*Semantic Information, Autonomous Agency and Non-equilibrium Statistical Physics*，Interface Focus 8，20180041。[DOI](https://doi.org/10.1098/rsfs.2018.0041)；[作者 PDF](https://artemyk.github.io/assets/pdf/papers/Kolchinsky_Wolpert_2018_Semantic%20information%2C%20autonomous%20agency%20and%20non-equilibrium%20statistical%20physics.pdf)；[本地原文](../../wiki/raw/round-04/L20-kolchinsky-wolpert-2018/original.pdf)。

核查 §§3–4 及 §5、§5.1.1，PDF pp. 5–7，并检查导论的问题定位。框架通过反事实打乱部分系统—环境信息，考察指定未来时刻的 viability 变化。相关性本身与相关性对持续性的贡献分开。

本篇选择负 Shannon 熵作为 viability，作者同时明说低熵不能保证处于指定存活集合，也不能保证保持身份，并讨论其他函数。其“语义”是特定物理框架内的功能性概念，不能直接替代语言意义或社会价值。对应 Q2，维护对象、身份和时间窗口仍需声明；本轮没有复现其信息最优化与数值例子。

## L21：统计物理的状态与单位

David Tong，*Lectures on Statistical Physics*，第 1 章 *The Fundamentals of Statistical Mechanics*。[剑桥大学章节原稿](https://www.damtp.cam.ac.uk/user/tong/statphys/one.pdf)；[本地 PDF](../../wiki/raw/round-04/L21-tong-statphys/original-native.pdf)。章节未核实独立出版年份，不推断为某年期刊文献。

核查 §1.2.1、§1.3.3，印刷 pp. 5、22–24 / PDF pp. 11、28–30。微正则状态计数、Gibbs 熵及正则分布具有各自的状态描述与约束。这个来源用于恢复物理含义及 J/K 单位，避免只看到 −Σp log p 的形式就把任意数据分布当作物理系统的完整熵。

## L22：复位热代价的实验

Antoine Bérut、Artak Arakelyan、Artyom Petrosyan、Sergio Ciliberto、Raoul Dillenschneider、Eric Lutz，2012，*Experimental Verification of Landauer’s Principle Linking Information and Thermodynamics*，Nature 483，187–189。[DOI](https://doi.org/10.1038/nature10872)；[大学存档](https://www.physics.rutgers.edu/~morozov/677_f2023/Physics_677_2023_files/Berut_Lutz_Nature2012.pdf)；[本地 PDF](../../wiki/raw/round-04/L22-berut-et-al-2012/original.pdf)。

核查期刊 pp. 187–189 / PDF pp. 1–3 的装置、复位步骤和平均热量。作者以双势阱中的胶体颗粒实现二态存储，研究操作时长与复位成功率。实验支持相应操作条件下接近 Landauer 下限，并讨论不完全复位的修正；个别轨迹和统计平均不能混淆。

这不是任意计算或组织运行耗电的实验，也没有测量“每 bit 每秒的普遍维持能耗”。本轮只依据正文报告解释证据范围，没有独立重算原始轨迹数据。

## 尚未覆盖

本轮没有系统综述算法复杂性、逻辑深度、所有网络复杂度、率失真理论、完整信息控制理论或社会价值理论。也没有证明跨领域统一标量不可能存在。本轮足以审查若干现有等同关系，后续统一理论还需要明确新对象、新机制及可区别于已有度量的预测。
