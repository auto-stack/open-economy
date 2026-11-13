# 组织持续综述的校准与试提取归档

2026年11月13日，Asia/Shanghai；请求时刻另按实际UTC保存。本批是framework-v0.1之后的新研究，不回写第1–37批来源包、旧manifest或既有原件。

| 编号 | 作品、取得状态与实际版本 | 本轮使用范围 |
|---|---|---|
| L195 | Conant与Ashby1970，DOI10.1080/00207727008920220；[大学重排本](L195-conant-ashby-1970/original.pdf)和[期刊扫描](L195-conant-ashby-1970/journal-scan.pdf)均已下载，各10页 | 期刊pp90–91、95–96选读；带封面扫描中p89＝PDF2，p95–96＝PDF8–9。重排本仅辅助文字定位，不套期刊页码；定理与限定页面已目视核查，未独立重证全部证明 |
| L196 | Bechtel与Bich2024，DOI10.1113/JP286883；原PDF多路径获取失败，[工具局部文字](L196-bechtel-bich-2024/partial-tool-text.txt)保留 | 出版社摘要／摘要图说明，以及机构库工具返回的作者稿p13、p15选段。未核对全篇、逐页对应或完整参考文献；PMID39383321，不采用搜索线索误关联的PMCID |
| L197 | Cross与Hohenberg1993，DOI10.1103/RevModPhys.65.851；[大学保存期刊PDF](L197-cross-hohenberg-1993/original.pdf)273页，期刊正文851–1112对应前262页 | 摘要、I.A开头p854、I.D选段pp858–859、II.A在p859的对流例；对应PDF1、4、8–9为选段。原式(2.1)核对p859。末11页及其余全文本轮未读 |
| L198 | Eykhoff1994，DOI10.4173/mic.1994.3.2；[出版社扫描PDF](L198-eykhoff-1994/original.pdf)5页 | 出版社摘要及首页p135，核对题名、作者、年份和引用1970原作的关系；未审查后四页控制模型。文字层只有DOI，正文不能据extracted.txt检索；不是L195重印 |

各作品的metadata.json、download-log.json及read-scope-extension.json记录取得范围、版本和SHA；原文件本地保存不等于许可公开再分发。

## 旧来源复用

L03、L05、L06、L14从原目录复用，原件及旧元数据不改写；本批[source-reuse.json](source-reuse.json)记录路径、原件哈希和本轮选读。旧范围保持，当前选段复核不覆盖旧读页，也不冒充新下载全文。

## 检索与拒收记录

discovery下保留网页搜索／打开回包、Crossref初始请求、三次429及顺序重试、适应性请求、OpenAlex校准、PubMed按DOI定位、EuropePMC核查和arXiv429。86次题录出现仅计Crossref76和OpenAlex10，不计可用性探测、网页发现或试提取样本；它们均非正式纳入结果。

有一次搜索资料页带来的PMCID实际对应其他论文：其HTML移至discovery/rejected-wrong-pmcid.html，保留[拒收说明](L196-bechtel-bich-2024/response-classification.json)，不作为L196原文。返回200而内容是拒绝页面／验证页的PDF请求也按失败处理，不能用文件后缀或HTTP状态认定全文取得。书章候选的重印关系尚待核查。

L196原PDF仍未取得，失败没有被缓存工具选段的存在抹去；其资料缺口进入下一阶段队列。检索命中但未采用的其他候选保留原始题录，不逐项标作已下载全文。

## 结果与保存方式

分析见[校准入口](../../../research/surveys/01-organization-maintenance/calibration-2026-11-13/README.md)、[重叠地图](../../../research/surveys/01-organization-maintenance/calibration-2026-11-13/existing-review-map.md)、[机制矩阵](../../../research/surveys/01-organization-maintenance/calibration-2026-11-13/pilot-extraction.md)及[第43轮说明](../../../research/reviews/43-maintenance-survey-calibration.md)。

[manifest.json](manifest.json)列本批实际文件及SHA-256（不自包含）。第三方原件、完整提取、原始回包和检查图按现有gitignore留在本地，原创分析、筛选决定、描述元数据与清单可进入版本管理。本轮未执行新的Git提交、标签或推送，旧ZIP不含第38、39批，不把新资料混称已打包。
