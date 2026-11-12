# 第一轮阅读与来源记录

日期：2026年11月11日。研究类型：先导性定向阅读。七项核心来源包含论文、理论讨论、讲演和教材，一项 NASA 材料补充火焰案例。下文只说明本轮实际核查的段落，未声称全书通读或系统覆盖该领域。

## 检索与筛选

使用网页搜索发现来源，以原论文、作者资料库、大学存档、Nobel Lecture 和原作者教材为依据。网络原文与检索结果存于 [wiki/raw](../../wiki/raw/round-01/README.md)。本轮先采用已有 Anderson、Simon 线索，再针对持续性、调节、自维持和边界问题补充材料。

| 批次 | 完整检索式 | 纳入与用途 |
|---|---|---|
| 01 | `Herbert Simon 1962 Architecture Complexity pdf near decomposable`；`Prigogine Nobel lecture 1977 time structure fluctuations pdf`；`Ashby introduction cybernetics 1956 pdf stability essential variables`；`Di Paolo 2005 autopoiesis adaptivity teleology agency pdf` | L02 至 L05，覆盖层级、耗散结构、调节及自维持与适应的区别 |
| 02 | `Montévil Mossio 2015 biological organisation closure constraints pdf`；`Coase nature firm 1937 pdf original`；`David Tong statistical physics phase transitions crystal spontaneous symmetry breaking`；`Prigogine Nobel lecture 1977 nobelprize pdf` | L06 提供对约束互相维护的明确框架；L07 检查经济领域所需的新增解释；L03 采用官方原文。Tong 留作后续线索，本轮未据其建立结论 |
| 03 | `Anderson More Is Different 1972 pdf`；`Ashby introduction cybernetics pdf rossashby.info`；`site.nasa.gov candle flame fuel oxygen combustion microgravity` | L01 与 L04 确定可下载原文；L08 核对火焰与环境关系 |

百科、社交平台、书评及二手介绍只用于发现线索，不作为结论依据。近年网络近可分解性研究、自创生计算及其他引用页未纳入正文阅读。没有进行数据库穷尽检索、年代分层或质量评分，本轮结果只满足专题先导研究的用途。

PDF 使用 PyMuPDF 提取并保留 PDF 页码标记，HTML 使用 BeautifulSoup 提取辅助文本。相关摘读保留段落或印刷页定位；扫描件采用目视阅读。原文件的版权声明保留，提取文本不替代原文。获取失败及副本差异单独记录。

## L01

P. W. Anderson，1972，*More Is Different*，Science 177(4047)，393–396。DOI：[10.1126/science.177.4047.393](https://doi.org/10.1126/science.177.4047.393)。[本地原文](../../wiki/raw/round-01/L01-anderson-1972/original.pdf)。

实际核查：p. 393 关于还原与从底层重建的区别；pp. 394–395 的晶体与对称性例子；p. 396 关于生物、文化类比的限制。对应 PDF 第 1 至 4 页，最后一页开始混入其他文章。

作者主张高层性质需要各层次的解释，随后借助对称破缺讨论物理例子。文末对进一步的生物文化类比保留明显限度。本轮据此限定跨层推理，不将其解释为“所有组织层级都由对称破缺产生”的证明。

## L02

Herbert A. Simon，1962，*The Architecture of Complexity*，Proceedings of the American Philosophical Society 106(6)，467–482。[本地原文](../../wiki/raw/round-01/L02-simon-1962/original.pdf)，[大学存档来源](https://www2.econ.iastate.edu/tesfatsi/ArchitectureOfComplexity.HSimon1962.pdf)。

实际核查：pp. 467–468 的复杂系统与层级定义；pp. 470–471 的稳定中间结构及其模型限制；pp. 474–475 的近可分解性和热交换例子。Iowa 副本含一页存档封面，印刷页 467 对应 PDF 第 2 页。

作者以非简单交互描述复杂系统，把层级作为重要结构线索；稳定中间结构和强弱交互差异分别支持形成与分析。p. 471 明确限制经典热力学对生物演化方向、速度的推断。相关模型支持有条件的层级研究，不能扩展成层级普遍必要性的定理。

## L03

Ilya Prigogine，1977，*Time, Structure and Fluctuations*，Nobel Lecture，12月8日。[官方来源](https://www.nobelprize.org/uploads/2018/06/prigogine-lecture.pdf)，[本地原文](../../wiki/raw/round-01/L03-prigogine-1977/original.pdf)。

实际核查：第 1 至 4 节，重点为印刷页 263–272，PDF 第 1 至 10 页。只记录宏观部分；未审查后半篇关于微观不可逆性的理论方案。公式的文字提取存在缺项，具体推导仍应核对 PDF。

讲演区分晶体式平衡结构与耗散结构，给出熵交换和内部产生的区分，并在相应近似下研究稳定性和化学模型。非平衡驱动能支持有序活动，但结果依赖动力学及边界条件。本轮据此区分结构保持和持续运行；不能从远离平衡直接推出自维持、最优化或适应。

## L04

W. Ross Ashby，1956，*An Introduction to Cybernetics*，Chapman & Hall。档案 PDF 为标注 1957 second impression 的版本。[作者档案来源](https://ashby.info/Ashby-Introduction-to-Cybernetics.pdf)，[本地原文](../../wiki/raw/round-01/L04-ashby-1956/original.pdf)。

实际核查：§3/11，pp. 39–41；§4/6–4/11，pp. 48–55；§5/1–5/6，pp. 73–77；§10/4–10/6，pp. 197–200。PDF 每页通常含两页印刷页，优先用节号定位。

系统描述需要选择变量；组成部分还须指定耦合方式。作者分别讨论集合保持、扰动及调节，以恒温水浴说明关键变量被限制在目标区间。由此可以操作化“维持什么、抵抗什么”；变量调节本身不包含调节器自我生产或修复的结论。

## L05

Ezequiel A. Di Paolo，2005，*Autopoiesis, Adaptivity, Teleology, Agency*，Phenomenology and the Cognitive Sciences 4，429–452。DOI：[10.1007/s11097-005-9002-y](https://doi.org/10.1007/s11097-005-9002-y)。[作者副本](https://ezequieldipaolo.net/wp-content/uploads/2011/10/autopoiesis_teleology_2005.pdf)，[本地原文](../../wiki/raw/round-01/L05-dipaolo-2005/original.pdf)。

实际核查：pp. 434–440，关于组织保持、主动调节、可生存范围与 adaptivity 的论证；对应 PDF 第 6 至 12 页。

本文在自创生研究内部，区分仍然保持组织与识别、应对失去生存条件的趋势。作者提出适应能力作为额外条件，也未要求达到最优状态。本轮据此审查“存在所以有维持本能”的推理；这是一项理论论证，不是所有组织已被实验验证的统一定义。

## L06

Maël Montévil 与 Matteo Mossio，2015，*Biological Organisation as Closure of Constraints*，Journal of Theoretical Biology 372，179–191。DOI：[10.1016/j.jtbi.2015.02.029](https://doi.org/10.1016/j.jtbi.2015.02.029)。[作者全文网页](https://montevil.org/publications/articles/2015-mm-organisation-closure-constraints/)，[本地网页](../../wiki/raw/round-01/L06-montevil-mossio-2015/original.html)。

实际核查：§1–2 的问题定位；§3 的约束定义；§4–5 的依赖与闭合；§6 至 §6.1 的边界讨论。采用作者网页章节定位，不假定它与期刊排版逐页一致。

作者按时间尺度区分过程和约束，用约束的相互维护刻画生物组织，并区分这种闭合与热力学隔离。其边界讨论仍依赖描述范围及依赖关系的识别。本轮把它作为自维持机制的有力候选框架；将其用于企业或一般物理结构仍需要额外论证。

## L07

R. H. Coase，1937，*The Nature of the Firm*，Economica 4(16)，386–405。DOI：[10.1111/j.1468-0335.1937.tb00002.x](https://doi.org/10.1111/j.1468-0335.1937.tb00002.x)。[大学扫描副本](https://msuweb.montclair.edu/~lebelp/coasenatfirmec1937.pdf)，[本地原文](../../wiki/raw/round-01/L07-coase-1937/original.pdf)。

实际核查：目视阅读 pp. 387–394，PDF 第 3 至 10 页；阅读拼图保存在来源目录。未进行全篇 OCR，`extracted.txt` 不含可用正文，不应据此做全文搜索或知识库正文导入。

作者从市场与企业协调方式的差别讨论企业存在，引入价格发现、缔约和内部组织成本。本轮借此识别社会经济连接所需的制度解释。对企业持续性的比较，应说明交易和组织关系；不能将企业直接认作生物闭合的实例。

## L08

NASA Biological and Physical Sciences，*Why NASA Is Studying Flames in Space*。[机构网页](https://science.nasa.gov/biological-physical/resources/explainers-infographics/why-nasa-is-studying-flames-in-space/)，[本地原文](../../wiki/raw/round-01/L08-nasa-candle/original.html)。页面未作为确定出版年份的依据。

实际核查：“What causes flames to behave differently in space?” 小节。NASA 对比地面和微重力中的火焰形态，说明环境和输运条件影响形态。该材料支持案例中的环境依赖性；并未证明火焰具有自主修复、自我生产或生物适应能力。

## 证据缺口

本轮足以提出定义候选和区分相关性质，但尚未比较自组织与自维持的全部流派。细胞的完整约束网络、企业的经验边界，以及火焰的定量维持模型均未在本轮重建。关于记忆、内部模型、演化筛选和统一度量的判断留待后续专题。
