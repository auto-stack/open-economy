"""Read-only audit of existing material; write derived local indexes and evidence.

No network, OCR, raw-source edits, model calls, user-data collection or payments.
"""
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
import csv
import datetime as dt
import hashlib
import json
import re
import time
import fitz

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "wiki/raw"
OUT = ROOT / "research/baselines/internal-knowledge-2026-11-12"
INDEX = ROOT / "wiki/index"
PROTOCOL = OUT / "protocol-v0.2.json"
digest_cache = {}


def rel(path):
    return path.relative_to(ROOT).as_posix()


def sha(path):
    path = path.resolve()
    if path not in digest_cache:
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        digest_cache[path] = h.hexdigest()
    return digest_cache[path]


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def table(path, records, fields=None):
    fields = fields or list(records[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in records:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                             for k, v in row.items() if k in fields})


def material_paths(meta_path, meta):
    """Keep declared and detected paths distinct; presence never means full reading."""
    pointers = {}
    for key in ("file", "archive_file", "archived_file"):
        if isinstance(meta.get(key), str):
            pointers[meta[key]] = ("declared:" + key, meta.get("sha256", ""))
    if isinstance(meta.get("source_file"), dict):
        x = meta["source_file"]
        if isinstance(x.get("file"), str):
            pointers[x["file"]] = ("declared:source_file", x.get("sha256", ""))
    for key in ("archived_files", "archived_documents", "source_files", "original_files"):
        for x in meta.get(key, []) if isinstance(meta.get(key), list) else []:
            if isinstance(x, dict) and isinstance(x.get("file") or x.get("path"), str):
                pointers[x.get("file") or x["path"]] = ("declared:" + key, x.get("sha256", ""))
    for p in meta_path.parent.glob("original*"):
        if p.is_file() and p.suffix.lower() in (".pdf", ".html", ".htm", ".txt", ".xml", ".json"):
            pointers.setdefault(p.name, ("detected_filename_only", ""))
    for name in ("web-tool-view.txt", "partial-web-tool-text.txt", "web-tool-text.partial.txt",
                 "bibliographic-tool.partial.txt", "tool-return-selected.txt"):
        if (meta_path.parent / name).is_file():
            pointers.setdefault(name, ("detected_partial_filename_only", ""))
    items = []
    for name, (basis, expected) in sorted(pointers.items()):
        p = (meta_path.parent / name).resolve()
        if not p.is_relative_to(RAW.resolve()):
            items.append({"path": name, "pointer_basis": basis, "status": "outside_raw_not_opened"})
            continue
        item = {"path": rel(p), "pointer_basis": basis, "exists": p.is_file()}
        if not p.is_file():
            item["status"] = "declared_file_missing"
            items.append(item)
            continue
        item.update(bytes=p.stat().st_size, sha256=sha(p))
        item["declared_hash_check"] = "match" if expected and expected == item["sha256"] else "mismatch" if expected else "not_declared"
        if p.suffix.lower() == ".pdf":
            with p.open("rb") as stream:
                item["pdf_header"] = b"%PDF-" in stream.read(1024)
            if item["pdf_header"]:
                try:
                    fitz.TOOLS.mupdf_warnings(reset=True)
                    with fitz.open(p) as doc:
                        counts = [len(doc[i].get_text().strip()) for i in range(min(6, len(doc)))]
                        item.update(pdf_pages=len(doc), text_sample_pages=list(range(1, len(counts) + 1)),
                                    text_sample_char_counts=counts,
                                    sample_sparse=len(counts) >= 2 and median(counts) < 100)
                    notice = fitz.TOOLS.mupdf_warnings(reset=True)
                    if notice:
                        item["pdf_processing_notice"] = notice
                except Exception as exc:
                    item["pdf_open_error"] = type(exc).__name__ + ": " + str(exc)
        items.append(item)
    return items


def main():
    started = time.perf_counter()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    INDEX.mkdir(parents=True, exist_ok=True)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8-sig"))
    fitz.TOOLS.mupdf_display_errors(False)
    sources, issues, corpus = [], [], []
    for p in sorted(RAW.glob("round-*/L*/metadata.json")):
        text = p.read_text(encoding="utf-8-sig")
        meta = json.loads(text)
        match = re.match(r"L(\d+)", str(meta.get("id") or p.parent.name))
        work_id = f"L{int(match[1]):02d}" if match else "unknown"
        payloads = material_paths(p, meta)
        failed = str(meta.get("download_status", "")).lower() in ("failed", "failed_response") or (
            isinstance(meta.get("status_code"), int) and meta["status_code"] >= 400)
        partial = any(word in str(meta.get("format", "")).lower() for word in ("partial", "connector")) or meta.get("full_article_archived") is False or any(
            "partial" in x.get("pointer_basis", "") or "partial" in x.get("path", "") or "tool-view" in x.get("path", "") for x in payloads)
        available = [x for x in payloads if x.get("exists")]
        lead_unavailable = not available and ("failed" in str(meta.get("download_status", "")).lower() or
            "lead" in str(meta.get("format", "")).lower() or "lead" in str(meta.get("selection_status", "")).lower())
        if failed or lead_unavailable:
            availability = "failed_acquisition_record"
        elif partial:
            availability = "partial_or_connector_material"
        elif any(x.get("pdf_header") for x in available):
            availability = "pdf_container_present_not_reading_claim"
        elif any(Path(x["path"]).suffix.lower() in (".html", ".htm") for x in available):
            availability = "html_or_record_container_not_fullwork_claim"
        elif available:
            availability = "other_material_present_scope_in_metadata"
        else:
            availability = "no_payload_identified_requires_review"
        scope = meta.get("read_scope") or meta.get("reading_scope") or ""
        version = meta.get("actual_version") or meta.get("archived_version") or meta.get("version") or ""
        row = {"record_id": rel(p), "work_id": work_id, "raw_id": meta.get("id", ""),
               "id_basis": "metadata" if meta.get("id") else "directory_inference_only",
               "title": meta.get("title", ""), "authors": meta.get("authors") or meta.get("author", ""),
               "publication": meta.get("publication", ""), "version_declared": version,
               "read_scope_declared": scope, "acquisition_status_declared": meta.get("download_status", ""),
               "original_downloaded_declared": meta.get("original_downloaded", meta.get("original_pdf_downloaded", "not_declared")),
               "availability_observed": availability, "selection_status_declared": meta.get("selection_status", ""),
               "text_status_declared": meta.get("text_status") or meta.get("text_extraction_status", ""),
               "reading_notes_declared": meta.get("reading_notes") or meta.get("version_and_reading_notes") or meta.get("notes", ""),
               "rights_notice_declared": meta.get("rights") or meta.get("license", ""),
               "redistribution_permission_assessed": False, "payloads": payloads, "metadata_sha256": sha(p)}
        sources.append(row)
        for key in ("title", "read_scope_declared"):
            if not row[key]:
                issues.append({"record_id": row["record_id"], "work_id": work_id, "issue": "missing_" + key,
                               "meaning": "获取失败/候选可能不适用，需区分，不自动补造", "action": "review_metadata_context"})
        if not meta.get("id"):
            issues.append({"record_id": row["record_id"], "work_id": work_id, "issue": "id_inferred_from_directory",
                           "meaning": "原元数据无id；派生目录保留推断依据", "action": "preserve_raw_and_label_candidate"})
        for x in payloads:
            if x.get("pdf_processing_notice"):
                issues.append({"record_id": row["record_id"], "work_id": work_id, "issue": "pdf_processing_notice",
                               "meaning": x["pdf_processing_notice"], "action": "inspect_rendering_before_ocr_or_repair_derived_copy"})
            if x.get("sample_sparse"):
                issues.append({"record_id": row["record_id"], "work_id": work_id, "issue": "sampled_pdf_text_sparse",
                               "meaning": "最多前6页文字层抽查稀疏，非全文OCR诊断", "action": "prioritize_ocr_or_explicit_scope_label"})
            if x.get("declared_hash_check") == "mismatch" or x.get("status") == "declared_file_missing":
                issues.append({"record_id": row["record_id"], "work_id": work_id, "issue": x.get("status", "metadata_hash_mismatch"),
                               "meaning": x["path"], "action": "investigate_without_overwriting_history"})
        corpus.append({"path": rel(p), "kind": "source_metadata", "title": str(meta.get("title") or p.parent.name),
                       "sha256": sha(p), "text": text})

    groups = defaultdict(list)
    for row in sources:
        groups[row["work_id"]].append(row)
    work_rows = []
    for work_id, variants in sorted(groups.items(), key=lambda x: int(x[0][1:])):
        ordered = sorted(variants, key=lambda x: (x["availability_observed"] == "failed_acquisition_record", x["record_id"]))
        work_rows.append({"work_id": work_id, "record_count": len(variants),
                          "record_ids": [x["record_id"] for x in variants],
                          "display_record": ordered[0]["record_id"],
                          "version_choice_required": len(variants) > 1,
                          "display_rule": "可用记录优先，仅用于目录展示；不合并读页或覆盖失败历史"})

    for base in ("book", "docs", "shared", "research"):
        for p in sorted((ROOT / base).rglob("*.md")):
            if rel(p) == "research/reviews/37-internal-knowledge-service-baseline.md":
                continue  # Current evaluation receipt must not leak into its own corpus.
            if p.name.lower() == "readme.md" or any(x in p.relative_to(ROOT).parts for x in ("history", "audits", "baselines")):
                continue
            text = p.read_text(encoding="utf-8-sig")
            corpus.append({"path": rel(p), "kind": "project_document_not_primary_evidence",
                           "title": next((s.lstrip("# ") for s in text.splitlines() if s.startswith("# ")), p.stem),
                           "sha256": sha(p), "text": text})
    corpus.sort(key=lambda x: x["path"])
    with (OUT / "corpus-snapshot.jsonl").open("w", encoding="utf-8") as stream:
        for row in corpus:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    archive_rows = []
    for p in sorted(RAW.glob("round-*/manifest.json")):
        value = json.loads(p.read_text(encoding="utf-8-sig"))
        entries = value if isinstance(value, list) else value.get("files", [])
        for x in entries:
            f = (p.parent / x["path"]).resolve()
            status = "outside_batch_not_opened"
            if f.is_relative_to(p.parent.resolve()):
                status = "missing" if not f.is_file() else "match" if sha(f) == x["sha256"] else "hash_mismatch"
            archive_rows.append({"manifest": rel(p), "path": x["path"], "expected_sha256": x["sha256"],
                                 "actual_sha256": sha(f) if f.is_file() and f.is_relative_to(p.parent.resolve()) else "", "status": status})
    table(OUT / "archive-integrity.csv", archive_rows)
    table(OUT / "metadata-quality-queue.csv", issues,
          ["record_id", "work_id", "issue", "meaning", "action"])
    with (INDEX / "source-catalog.jsonl").open("w", encoding="utf-8") as stream:
        for row in sources:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    table(INDEX / "source-catalog.csv", sources, [k for k in sources[0] if k != "payloads"])
    dump(INDEX / "work-groups.json", work_rows)

    rankings, results = [], []
    for case in protocol["cases"]:
        candidates = []
        for doc in corpus:
            body, title = doc["text"].casefold(), doc["title"].casefold()
            counts = [body.count(term.casefold()) for term in case["terms"]]
            matched = [term for term, count in zip(case["terms"], counts) if count]
            score = 6 * len(matched) + 2 * sum(term.casefold() in title for term in case["terms"]) + sum(min(c, 3) for c in counts)
            if score:
                lines = doc["text"].splitlines()
                hits = [{"line": n, "text": line[:260]} for n, line in enumerate(lines, 1)
                        if any(t.casefold() in line.casefold() for t in case["terms"])][:4]
                candidates.append({"path": doc["path"], "kind": doc["kind"], "score": score,
                                   "matched_terms": matched, "snippet_lines": hits})
        candidates.sort(key=lambda x: (-x["score"], x["path"]))
        top = candidates[:protocol["search_method"]["top_k"]]
        ranks = [n for n, row in enumerate(candidates, 1) if row["path"] in case["expected_paths"]]
        rankings.append({"id": case["id"], "question": case["question"], "terms": case["terms"], "top_results": top})
        results.append({"id": case["id"], "question": case["question"], "terms": case["terms"],
                        "first_expected_file_rank": min(ranks) if ranks else "not_found",
                        "expected_file_in_top10": any(row["path"] in case["expected_paths"] for row in top),
                        "top1_path": top[0]["path"] if top else "", "evaluation_type": "assisted_term_file_location_not_QA_accuracy"})
    dump(OUT / "rankings.json", rankings)
    table(OUT / "file-location-results.csv", results)
    raw_files = [p for p in RAW.rglob("*") if p.is_file()]
    summary = {"version": "0.2", "catalogue_normalization_revision": 2, "date_local": "2026-11-12", "started_utc": started_utc,
               "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "local_processing_seconds": round(time.perf_counter() - started, 4),
               "protocol_sha256": sha(PROTOCOL), "source_metadata_records": len(sources),
               "work_identifier_slots_including_failed_candidates": len(groups),
               "duplicate_identifier_groups": [x for x in work_rows if x["record_count"] > 1],
               "source_container_states": dict(Counter(x["availability_observed"] for x in sources)),
               "quality_queue_counts": dict(Counter(x["issue"] for x in issues)),
               "archive_manifest_count": len(list(RAW.glob("round-*/manifest.json"))),
               "archive_hash_status_counts": dict(Counter(x["status"] for x in archive_rows)),
               "raw_file_count": len(raw_files), "raw_bytes": sum(p.stat().st_size for p in raw_files),
               "retrieval_corpus_records": len(corpus), "project_document_count": sum(x["kind"] != "source_metadata" for x in corpus),
               "file_location_cases": len(results), "file_location_top10_hits": sum(x["expected_file_in_top10"] for x in results),
               "raw_sources_modified": False, "new_network_sources": 0, "OCR_executed": False,
               "formal_register_sha256": sha(ROOT / "shared/theory-register.md"),
               "limits": "One local processing run, not human labor time, service latency, natural-language accuracy, independent review, scientific truth or commercial feasibility."}
    dump(OUT / "summary.json", summary)
    fitz.TOOLS.mupdf_display_errors(True)
    print(json.dumps({"source_records": len(sources), "work_slots": len(groups),
                      "archive": summary["archive_hash_status_counts"], "quality": summary["quality_queue_counts"],
                      "corpus": len(corpus), "results": [{k: r[k] for k in ("id", "first_expected_file_rank", "expected_file_in_top10", "top1_path")} for r in results],
                      "processing_seconds": summary["local_processing_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
