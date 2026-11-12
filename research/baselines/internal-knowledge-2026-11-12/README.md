# 内部资料与质量基线 v0.2

日期：2026年11月12日。范围依用户回复限定为内部资料与质量，不核算真实经营、收费或资金可行性。

先读[报告](../../reviews/37-internal-knowledge-service-baseline.md)、[八项证据回答](answers-and-evidence.md)和[维护工作观察](maintenance-and-observation.md)。可用资料入口是[来源目录](../../../wiki/index/SOURCES.md)，完整字段在[结构化索引](../../../wiki/index/README.md)。

## 本轮执行材料

| 文件 | 作用 |
|---|---|
| [protocol-v0.2.json](protocol-v0.2.json) | 执行前固定问题、显式词项、范围与判断限制；原v0.1保留原文件 |
| [corpus-snapshot.jsonl](corpus-snapshot.jsonl) | 151项目文档＋193元数据的完整索引用文字和哈希，不含原论文正文或本轮答案 |
| [rankings.json](rankings.json)、[定位表](file-location-results.csv) | 八题前10项及预定文件首次出现位置；不作自动问答准确率 |
| [逐题复核](scope-review.csv) | 同一助手的证据与范围核对，非独立评分 |
| [archive-integrity.csv](archive-integrity.csv) | 36批清单列明的1,117文件校验，全部匹配 |
| [manifest-coverage.json](manifest-coverage.json) | 其余60文件分类，不将清单／回执／缓存作论文原件 |
| [metadata-quality-queue.csv](metadata-quality-queue.csv) | 缺项、扫描抽样与解析提示，保留出处 |
| [pdf-processing-notices.json](pdf-processing-notices.json)、[render-checks.json](render-checks.json) | 21份解析提示；三份PDF共五页的视觉抽查，不证明全篇无误 |
| [L144定向诊断](L144-targeted-diagnostics.json) | 文字层提示与选页可见性分开记录 |
| [summary.json](summary.json) | 本次机器处理、数量、范围及限制，不作为人工工时或实际报价 |
| [first-run](first-run) | 旧字段映射尚未补齐的首轮结果，保留修订过程 |

目录映射补充只改善已有载荷的识别，没有覆盖raw或改变词项定位结果。后续重跑如输入变化，需另存新协议与快照，不能把不同输入下的耗时或结果当作同一次基线。

本轮未新增网络研究，raw批次数仍为36，来源编号未增加，书稿仍十一章、28候选单元，正式理论79条保持。没有执行OCR、独立用户试验、真实维护付款或AutoDown导入。
