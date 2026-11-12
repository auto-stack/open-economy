"""Index reused source originals for the eight human-route manuscript chapters."""
from pathlib import Path
import re,json,hashlib,datetime

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'wiki/raw/round-17'
OUT.mkdir(parents=True,exist_ok=True)
USES={
 'L05':('状态 趋势及适应能力的理论区分','13-human-maintenance-objects.md'),
 'L06':('构成维护及约束关系的组织分析入口','01-reading-notes.md'),
 'L37':('实际规则 行动情境与结果的框架区分','07-reading-notes.md'),
 'L51':('合作演化的机制地图，未重建全部证明','11-human-cooperation-direction.md'),
 'L55':('目标内容 动机方式及内化的领域区分','12-reading-notes.md'),
 'L56':('合作群体形成与进一步生物整合分开','12-reading-notes.md'),
 'L57':('共同意向与角色理解的候选机制','12-reading-notes.md'),
 'L59':('特定实验中惩罚与共同投入的联系及成本','12-reading-notes.md'),
 'L60':('反社会惩罚及惩罚后果的范围限制','12-reading-notes.md'),
 'L61':('生理调节 多回路与中央整合模型的边界','12-reading-notes.md'),
 'L62':('基本能力 实际机会与资源的规范分析','13-human-maintenance-objects.md'),
 'L64':('狭义想要与愉快分开，不采用临床推断','14-reading-notes.md'),
 'L65':('特定奖励学习中的预期与误差模型','14-reading-notes.md'),
 'L67':('控制指定与执行区分，EVC及主观努力成本的条件','15-reading-notes.md'),
 'L69':('目标脱离与重新投入的区分，保留横断面限制','15-reading-notes.md'),
 'L70':('目标意向与实施意向分开，不采用固定效果倍数','15-reading-notes.md'),
 'L73':('不完全合同的修订与事前投资激励，限定模型','16-reading-notes.md'),
 'L74':('个人所得与继续帮助伙伴的任务差异，保留替代解释','16-reading-notes.md'),
 'L75':('权威信念 道德判断与规范评价的区别，仅部分工具正文','17-reading-notes.md'),
 'L76':('意义的主客观关系及更大事物观的哲学讨论','17-reading-notes.md'),
 'L77':('主观意义的连贯 目的与价值感三分框架','17-reading-notes.md'),
 'L78':('有意义工作的自报关联，保留文化 样本及因果限制','17-reading-notes.md'),
}
records={};chapter_rows=[]
chapters=sorted((ROOT/'book/part-02').glob('*.md'))+sorted((ROOT/'book/part-03').glob('*.md'))
for chapter in chapters:
 text=chapter.read_text(encoding='utf-8');title=text.splitlines()[0].removeprefix('# ')
 source_ids=[]
 for link in re.findall(r'\]\(([^)]+)\)',text):
  if 'wiki/raw/round-' not in link or '://' in link:continue
  source=(chapter.parent/link.split('#')[0]).resolve()
  assert source.is_file(),source
  sid_match=re.match(r'(L\d+)-',source.parent.name)
  if not sid_match:continue
  sid=sid_match.group(1);source_ids.append(sid)
  if sid not in records:
   mp=source.parent/'metadata.json';meta=json.loads(mp.read_text(encoding='utf-8'));data=source.read_bytes();sha=hashlib.sha256(data).hexdigest()
   if meta.get('sha256'):assert meta['sha256']==sha,(sid,'original differs from source metadata')
   scope=meta.get('read_scope') or meta.get('reading_scope') or 'See retained reading notes for actual targeted scope.'
   records[sid]={'source_id':sid,'title':meta.get('title'),'original':'../'+source.relative_to(ROOT/'wiki/raw').as_posix(),'source_metadata':'../'+mp.relative_to(ROOT/'wiki/raw').as_posix(),'source_url':meta.get('source_url') or meta.get('final_url') or meta.get('url') or meta.get('requested_url'),'actual_material_type':meta.get('format') or source.suffix.removeprefix('.'),'full_original_archived':sid!='L75','retained_version':meta.get('version') or meta.get('archived_version') or meta.get('publication'),'prior_read_scope':scope,'reading_notes':'../../../research/reviews/'+USES[sid][1],'chapter_reuse_scope':USES[sid][0],'new_download_this_round':False,'new_primary_reading_this_round':False,'bytes':len(data),'sha256':sha,'chapters':[]}
  cp='../../../'+chapter.relative_to(ROOT).as_posix()
  if cp not in records[sid]['chapters']:records[sid]['chapters'].append(cp)
 chapter_rows.append({'chapter':'../../../'+chapter.relative_to(ROOT).as_posix(),'title':title,'sources':sorted(set(source_ids),key=lambda x:int(x[1:]))})
sources=sorted(records.values(),key=lambda x:int(x['source_id'][1:]))
assert len(chapters)==8 and len(sources)==22,(len(chapters),len(sources))
catalog={'date_local':'2026-11-12','timezone':'Asia/Shanghai','purpose':'Source reuse for the human-to-meaning manuscript route, not a new literature search or new full-text acquisition.','new_network_sources':0,'new_full_originals':0,'reused_sources':len(sources),'full_originals_reused':sum(x['full_original_archived'] for x in sources),'partial_tool_text_sources_reused':sum(not x['full_original_archived'] for x in sources),'sources':sources,'chapters':chapter_rows}
(OUT/'source-reuse.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 人类路线整理入书的来源复用','','日期：2026年11月12日。对应[八章目录](../../../book/README.md)与[纲领0.3](../../../docs/charter.md)。本轮将既有研究写入书中，没有新增网络来源、重新下载原文或新增逐篇原文阅读。研究笔记与书稿相互校核不计为新来源阅读。','','采用22项既有来源，其中21项已有原始全文文件，一项L75仍只有部分工具正文。原文件继续保存在原批次；本目录保存复用关系与校验，不以摘要替代原文，也不将重复引用计为新增全文。','','## 来源与章节用途','','| 来源 | 本轮章节用途 | 原档案与范围 |','|---|---|---|']
for s in sources:
 lines.append(f"| {s['source_id']} | {s['chapter_reuse_scope']} | [实际材料]({s['original']})；[原元数据]({s['source_metadata']})；[阅读记录]({s['reading_notes']}) |")
lines+=['','## 八章对应','','| 章节 | 来源编号 |','|---|---|']
for c in chapter_rows:lines.append(f"| [{c['title']}]({c['chapter']}) | {', '.join(c['sources'])} |")
lines+=['','## 版本与证据边界','','L51为论文网页打印副本；L56为Early Edition；L57为录用稿；L61为NCBI全文转换XML；L62与L76为官方讲演HTML；L73为1988年期刊版本；L75原PDF未取得，部分工具正文不能标成完整下载。L76也不是2010年同名书。实际读取范围沿用原元数据与研究记录，未因进入书稿而扩大。','','L71、L72、L68未取得论文正文，SuperCooperators只有出版线索，均没有作为本轮书稿具体结论的证据。L63、L66的具体实验结果也未纳入八章。既有学习、承诺与意义研究不拼接成一个已经证实的完整人性模型。','','正文分别标明工作概念、条件推论、文献结果、待验证假说、哲学解释及价值主张。课程合作是解释性假设，不是运行数据。推论的现实前提、规范理由及Open Business效果分别论证，正式79条总表未改变。','','## 复核与导入','','[source-reuse.json](source-reuse.json)记录原文件网址、实际类型、版本、原读取范围、章节用途、相对路径、字节数和SHA-256；L75的哈希对应工具文本，不是未取得的PDF。[manifest.json](manifest.json)校验本目录记录，原文件哈希另由复用清单逐一核查。原始版权与许可声明继续保留，本地研究用途不自动产生公开再分发许可。','','AutoDown导入时可按来源编号及哈希关联已有原文，保留部分获取状态与版本区别。历史书稿和0.2纲领不是新的外部来源，分别保存在book/history和docs/history，其元数据记录原文件校验。']
(OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
files=[]
for p in sorted(OUT.iterdir()):
 if not p.is_file() or p.name=='manifest.json':continue
 data=p.read_bytes();files.append({'path':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(OUT/'manifest.json').write_text(json.dumps({'date_local':'2026-11-12','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_network_sources':0,'new_full_originals':0,'reused_sources':22,'files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manuscript_chapters':len(chapters),'reused_sources':len(sources),'full_originals_reused':catalog['full_originals_reused'],'partial_tool_text_sources_reused':catalog['partial_tool_text_sources_reused'],'source_hashes_verified':len(sources)},ensure_ascii=False))
