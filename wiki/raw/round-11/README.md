# 人 合作与规范的首轮资料归档

研究日期：2026年11月12日，Asia/Shanghai。机器获取时间按UTC记录，部分为11月11日。对应[研究结论](../../../research/reviews/12-human-bridge-findings.md)与[阅读笔记](../../../research/reviews/12-reading-notes.md)。

本批取得八项新增学术来源：七份PDF与一份NCBI BioC全文XML。保留原格式、提取文本、元数据及失败尝试。下载全文与实际阅读范围分别记录；本轮是定向阅读，尚非系统综述或所有来源的全文精读。

| 来源 | 内容 | 实际保存版本 |
|---|---|---|
| [L54 Sterling 2012](L54-sterling-2012/metadata.json) | 预测性生理调节 | 12页PDF；含1页ResearchGate封面和11页期刊论文，镜像副本 |
| [L55 Deci与Ryan 2000](L55-deci-ryan-2000/metadata.json) | 心理需要 目标与动机 | 42页期刊论文，SDT网站副本 |
| [L56 West等2015](L56-west-et-al-2015/metadata.json) | 合作与重大个体性转变 | 8页PNAS Early Edition，大学作者副本 |
| [L57 Tomasello等2005](L57-tomasello-et-al-2005/metadata.json) | 共同意向与文化认知 | 42页录用后的出版前稿，首页©2004、in press；不是最终期刊排印版 |
| [L58 Henrich等2005](L58-henrich-et-al-2005/metadata.json) | 跨文化行为实验与争议 | 62页作者校样，含评论及答复；有编辑标记和占位页码 |
| [L59 Fehr与Gächter 2002](L59-fehr-gaechter-2002/metadata.json) | 承担成本的惩罚与合作 | 4页Nature排印版，LMU仓储副本；2003仓储编号不等于发表年份 |
| [L60 Herrmann等2008](L60-herrmann-et-al-2008/metadata.json) | 对合作贡献者的惩罚 | 6页Science排印副本，首尾含相邻论文片段，不作为本篇证据 |
| [L61 Ramsay与Woods 2014](L61-ramsay-woods-2014/metadata.json) | 稳态与异稳态概念争议 | PMC作者稿的NCBI BioC全文XML；没有取得排印PDF，交叉引用可能简化 |

原文位于各来源目录的 `original.pdf` 或 `original.xml`，辅助文本为 `extracted.txt`。L57、L58首页另有渲染图用于核查版本，不代替原文。各项阅读位置见元数据与研究笔记，L61按小节而非虚构PDF页码定位。

## 获取失败与替代来源

L57和L58最初的MPI链接返回404，响应体保留为 `failed-response-initial.bin`；它们不是论文。L57的UVA实验室链接返回403，作者主页提供的公开Drive文件连接超时，随后取得出版前副本。L58的Harvard PDF链接返回404，随后取得UBC作者校样。L59首次镜像因证书验证失败，未关闭证书验证，改用LMU仓储。

L61的PMC网页返回HTTP 200但正文是浏览器检查页，保存为 `response-pmc.html`，不标作全文；另一镜像返回405。随后通过NCBI公开BioC全文接口取得并解析作者稿XML，没有绕过验证码或受限登录。各来源的 `acquisition-log.json` 汇总尝试，并保留原始尝试文件；部分早期404记录从本轮工具结果回填，回填标记写入日志。

## 校验与后续导入

[manifest.json](manifest.json)列出八项原文及本批辅助文件的字节数和SHA-256，清单本身与缓存不计入自身校验。元数据记下DOI、下载网址、实际版本、取得时间及阅读范围；未来转换到AutoDown时保留这些字段。XML可按passage及offset恢复分段，PDF表格、公式和扫描信息须回原文核查。

六份 `search-*.json` 保存检索返回。检索命中不等于采用；未读未采用的网页只作线索，不全部下载。L51与L52复用[上一批资料](../round-10/README.md)，不重复计数；SuperCooperators仍只有书目核查，没有取得全书。

随后讨论“人作为组织”时追加 `search-07-human-organization-discussion.json`，复核已归档L55与L61的网络入口；不新增全文来源，也不改变此前的实际阅读范围记录。

原作版权与许可声明保留；本地研究存档不赋予公开再分发许可。分析、模型与研究判断位于research目录，与本批原文分开。
