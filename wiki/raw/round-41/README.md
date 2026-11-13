# 原始调节论述与2026年后续资料归档

2026年11月13日，Asia/Shanghai。服务[2026年资料综述0.3](../../../research/surveys/01-organization-maintenance/review-2026.md)，补充关键原始概念论述及2026年研究。7个资料编号中，3项取得完整文献并选读，4项为原作者摘要或出版社预览，不以网页体积、参考文献可见或HTTP200认定全文取得。

| 编号与作品 | 实际取得 | 本轮阅读和边界 |
|---|---|---|
| L204 Partridge1982，The good enough calculi of evolving control systems，DOI10.1152/ajpregu.1982.242.3.R173 | [PubMed原摘要XML](L204-partridge-1982/pubmed.xml)，出版社PDF403 | 仅摘要；不重建原文的控制逻辑。与第40批discovery的同一PubMed摘要对应，作品此轮登记编号，不重复算独立证据 |
| L205 Moore-Ede1986，Physiology of the circadian timing system，DOI10.1152/ajpregu.1986.250.5.R737 | [PubMed原摘要XML](L205-moore-ede-1986/pubmed.xml)，出版社403、CiteSeer路径超时 | 仅摘要中的预期／反应区分及预期失配观点；正文实验未取得 |
| L206 Romanovsky2004，Do fever and anapyrexia exist?，DOI10.1152/ajpregu.00068.2004 | [作者实验室完整PDF](L206-romanovsky-2004/original.pdf)，4页，R992–R995 | 读正文及图1，图已目视核查；作者汇总的具体原实验未独立重查。否定特定定义不等于否认升／降温现象 |
| L207 Weinberger2026，Homeostasis and causal control，DOI10.1007/s10539-026-10018-8 | [出版社完整PDF](L207-weinberger-2026/original.pdf)，30页 | PDF1、9–13、22–24、27选段；目视核对PDF9和23公式。文字层含inline-eq等占位符，仅作搜索辅助，不能直接导入为正确公式；未独立复现完整模型 |
| L208 Burggren／Wang2026，Beyond canonical homeostasis，DOI10.14814/phy2.71150 | [EuropePMC完整JATS XML](L208-beyond-2026/original.xml)及[PMC HTML](L208-beyond-2026/original.html)，PDF未取得 | 核对DOI／PMCID／PMID；读§1.2、§3.1.2、§4.1–4.2、§5–6。综述案例与节能演化假说分开，不把间歇自动视为适应或节能 |
| L209 Rama2026，Autonomy and development，DOI10.1007/s10539-026-10007-x | [出版社摘要与预览HTML](L209-development-2026/original.html)；正文未取得，机构库返回拒绝页 | 仅Abstract；其发育批评作为待读问题，不展开未读框架与图示 |
| L210 Kanosue等，Concepts to utilize in describing thermoregulation，DOI10.1007/s00421-009-1256-6 | [出版社摘要与预览HTML](L210-kanosue-2010/original.html)，2009在线、2010卷109:5–11；PDF未取得 | 仅Abstract；多回路、前馈及其他生理需求的观点按摘要范围采用，神经生理和实验细节待核 |

各资料的metadata.json、download-log.json与read-scope-extension.json记录URL、SHA、实际版本、内容状态和读段。原PDF保留版权；保存到本地不代表取得公开再分发许可。

## 获取与内容辨认

L206的HTTPS作者站点证书过期，随后从同一公开作者实验室的HTTP文档路径成功取得期刊版，按标题、作者、DOI及R992–R995页码核对；两次尝试均保留。未关闭证书验证。

L208的BioC请求返回no-result帮助页，原响应移至discovery/rejected-bioc-error.html，未作为XML正文。后由EuropePMC取得JATS，验证article根节点及DOI10.14814/phy2.71150、PMCID PMC13681041、PMID42897941。XML的pub-date为2026-10-19，OpenAlex显示2026-10-01，两个来源分别记录，不静默统一日期。完整XML不代表已下载其所有图像资产。

L209及L210保存的是实际出版社HTML，但页上只有摘要、预览与书目信息等，没有取得正文；response-classification.json记录这一点。L209的repository-response.html是244字节拒绝响应，不是作者稿。L207的PDF可以正常阅读关键页面，公式文字层的缺陷另记，不以提取乱码填公式。

discovery保留4组网页检索回包、打开结果、OpenAlex定位和4组实际获取尝试。它们是定向发现与引用追读，不是新增一轮完整数据库系统筛选；获取失败、摘要、全文与阅读分别计数。

## 与书籍资料的关系

[阅读与论证边界](../../../research/surveys/01-organization-maintenance/primary-followup-2026-11-13/reading-notes.md)、[状态表](../../../research/surveys/01-organization-maintenance/primary-followup-2026-11-13/source-status.csv)、[章节对应](../../../research/surveys/01-organization-maintenance/primary-followup-2026-11-13/chapter-mapping.md)及[第46轮说明](../../../research/reviews/46-primary-regulation-and-2026.md)说明本批用途。旧综述0.2保留，旧第38–40批和框架来源包不回写。

[manifest.json](manifest.json)列本批文件字节与SHA，不自包含；第三方原件、提取、API回包及检查图按现有gitignore留在本地，来源描述与原创分析可纳管。本轮未进行新的Git提交、标签、推送或对外发布。
