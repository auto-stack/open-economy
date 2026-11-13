"""A transparent structured-record comparison, not a human reader benchmark."""
from pathlib import Path
import copy
import hashlib
import json
import math
import random

HERE = Path(__file__).resolve().parent


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixture():
    claims, records = [], []

    def add(cid, kind, **fields):
        item = {'id': f'{cid}-{kind}', 'owner': cid, 'kind': kind, **fields}
        records.append(item)
        return item['id']

    for i in range(1, 8):
        cid = f'C{i:02}'
        curve = i in [4, 5, 7]
        scope = ({'task': 'bounded-curve', 'context': 'A', 'x_range': [0, 1], 'unit': 'U', 'tolerance': .1}
                 if curve else {'task': 'sample-mean', 'context': 'sample-S1', 'unit': 'U'})
        value = None if curve else (6 if i in [1, 2] else 4)
        statement = ('环境A、0≤x≤1时，y=x²的误差不超过0.1U。' if curve else
                     f'样本S1中三个值的算术均值为{value}U；没有声称总体或未来均值。')
        claims.append({'id': cid, 'text': statement, 'declared_scope': scope, 'reported_value': value})
        data = add(cid, 'data', values=None if curve else [2, 4, 6],
                   observations=[[0, 0], [1, 1], [.5, .25], [.75, .5625]] if curve else None,
                   unit='U', context=scope['context'])
        procedure = add(cid, 'procedure', operation='square' if curve else ('sum/(n-1)' if i == 1 else 'sum/n'))
        add(cid, 'run', data_ref=data, procedure_ref=procedure,
            output=None if curve else (6 if i == 1 else 4), version='v1' if i == 1 else 'v2')
        add(cid, 'scope', **scope)
        if i in [5, 7]:
            add(cid, 'observation', x=.5, y=.4, context='A' if i == 5 else 'B', unit='U')
    return claims, records


def questions():
    return [{'claim_id': f'C{i:02}',
             'request': {'task': ('population-forecast' if i == 3 else 'bounded-curve' if i in [4, 5, 7] else 'sample-mean'),
                         'context': 'A' if i in [4, 5, 7] else 'sample-S1',
                         'unit': 'U', 'x': 1.5 if i == 4 else .75 if i in [5, 7] else None}}
            for i in range(1, 8)]


def expected_answers():
    # Reference decisions are not exposed to the reader below or the index builder.
    return {'C01': {'status': 'procedure-error', 'locations': ['C01-procedure']},
            'C02': {'status': 'claim-run-mismatch', 'locations': ['C02', 'C02-run']},
            'C03': {'status': 'outside-declared-scope', 'locations': ['C03']},
            'C04': {'status': 'outside-declared-scope', 'locations': ['C04']},
            'C05': {'status': 'conflicting-evidence', 'locations': ['C05-observation']},
            'C06': {'status': 'usable-in-finite-task', 'locations': []},
            'C07': {'status': 'usable-with-other-context-anomaly', 'locations': ['C07-observation']}}


def build_index(path):
    groups, entries, inspected = {}, {}, 0
    with path.open('rb') as stream:
        while True:
            offset = stream.tell()
            line = stream.readline()
            if not line:
                break
            record = json.loads(line)
            groups.setdefault(record['owner'], []).append(record['id'])
            entries[record['id']] = {'offset': offset, 'bytes': len(line)}
            inspected += 1
    return {'snapshot_sha256': sha(path.read_bytes()), 'groups': groups, 'entries': entries}, {
        'record_inspections': inspected, 'index_entries_written': len(entries),
        'read_bytes': path.stat().st_size}


def within(scope, request):
    if any(scope[k] != request[k] for k in ['task', 'context', 'unit']):
        return False
    return 'x_range' not in scope or scope['x_range'][0] <= request['x'] <= scope['x_range'][1]


def interpret(claim, records):
    """Same fixed semantic checks for B and C; no reference-answer access."""
    by_kind = {r['kind']: r for r in records if r['kind'] != 'observation'}
    if not {'data', 'procedure', 'run', 'scope'} <= by_kind.keys():
        return {'status': 'insufficient-evidence', 'locations': []}
    data, proc, run, scope = (by_kind[k] for k in ['data', 'procedure', 'run', 'scope'])
    if run['data_ref'] != data['id'] or run['procedure_ref'] != proc['id']:
        return {'status': 'reference-mismatch', 'locations': [run['id']]}
    if {k: scope[k] for k in claim['declared_scope']} != claim['declared_scope']:
        return {'status': 'scope-record-mismatch', 'locations': [claim['id'], scope['id']]}
    if scope['task'] == 'sample-mean':
        values = data['values']
        computed = sum(values) / (len(values) - 1 if proc['operation'] == 'sum/(n-1)' else len(values))
        intended = sum(values) / len(values)
        if computed != intended:
            return {'status': 'procedure-error', 'locations': [proc['id']], 'replay': computed, 'intended': intended}
        if claim['reported_value'] != run['output']:
            return {'status': 'claim-run-mismatch', 'locations': [claim['id'], run['id']]}
        return {'status': 'usable-in-finite-task', 'locations': []}
    anomalies = [r for r in records if r['kind'] == 'observation']
    conflicts = [r for r in anomalies if r['context'] == scope['context'] and r['unit'] == scope['unit']
                 and scope['x_range'][0] <= r['x'] <= scope['x_range'][1]
                 and abs(r['y'] - r['x'] ** 2) > scope['tolerance']]
    if conflicts:
        return {'status': 'conflicting-evidence', 'locations': [r['id'] for r in conflicts]}
    if anomalies:
        return {'status': 'usable-with-other-context-anomaly', 'locations': [r['id'] for r in anomalies]}
    return {'status': 'usable-in-finite-task', 'locations': []}


def answer(claim, question, mode, path, index, budget=None):
    cost = {'conclusion_records': 1, 'evidence_records_read': 0, 'evidence_bytes_read': 0,
            'index_lookups': 0}
    trace, records = [], []
    if not within(claim['declared_scope'], question['request']):
        return {'status': 'outside-declared-scope', 'locations': [claim['id']], 'cost': cost, 'trace': trace}
    if mode == 'A':
        return {'status': 'insufficient-evidence', 'locations': [], 'cost': cost, 'trace': trace}
    if mode == 'C':
        cost['index_lookups'] += 1
        with path.open('rb') as stream:
            for rid in index['groups'].get(claim['id'], []):
                if budget is not None and cost['evidence_records_read'] >= budget:
                    return {'status': 'budget-exhausted', 'locations': [], 'cost': cost, 'trace': trace}
                stream.seek(index['entries'][rid]['offset'])
                line = stream.readline()
                r = json.loads(line)
                cost['evidence_records_read'] += 1
                cost['evidence_bytes_read'] += len(line)
                trace.append(r['id'])
                if r['id'] != rid or r['owner'] != claim['id']:
                    return {'status': 'index-requires-review', 'locations': [rid], 'cost': cost, 'trace': trace}
                records.append(r)
    else:
        with path.open('rb') as stream:
            for line in stream:
                if budget is not None and cost['evidence_records_read'] >= budget:
                    return {'status': 'budget-exhausted', 'locations': [], 'cost': cost, 'trace': trace}
                r = json.loads(line)
                cost['evidence_records_read'] += 1
                cost['evidence_bytes_read'] += len(line)
                trace.append(r['id'])
                if r['owner'] == claim['id']:
                    records.append(r)
    verdict = interpret(claim, records)
    return {**verdict, 'cost': cost, 'trace': trace}


def summarize(rows, gold):
    costs = {k: sum(r['cost'][k] for r in rows) for k in rows[0]['cost']}
    return {'questions': len(rows),
            'reference_decisions_resolved': sum(r['status'] == gold[r['claim_id']]['status'] for r in rows),
            'exact_error_locations': sum(r['locations'] == gold[r['claim_id']]['locations']
                                         and r['status'] == gold[r['claim_id']]['status'] for r in rows
                                         if r['claim_id'] in ['C01', 'C02', 'C05']),
            'error_location_tasks': 3,
            'unsafe_acceptances_in_fixture': sum(r['status'].startswith('usable')
                                                and not gold[r['claim_id']]['status'].startswith('usable') for r in rows),
            'abstentions_or_budget_stops': sum(r['status'] in ['insufficient-evidence', 'budget-exhausted',
                                                             'index-requires-review'] for r in rows), 'cost': costs}


def run():
    conclusions, original_records = fixture()
    qs, gold = questions(), expected_answers()
    save(HERE / 'fixtures/conclusions.json', conclusions)
    save(HERE / 'fixtures/questions.json', qs)
    save(HERE / 'fixtures/reference-decisions.json', gold)
    results = {'kind': 'scripted internal comparison, synthetic records, no human timing or population accuracy',
               'layout_seed': 20261113, 'scenarios': [], 'faults': {}, 'cost_sensitivity': []}
    for noise in [0, 20, 100]:
        records = copy.deepcopy(original_records)
        records += [{'id': f'Z{k:03}', 'owner': 'unrelated', 'kind': 'note',
                     'text': '辅助背景材料，不支持本轮七项主张。'} for k in range(noise)]
        random.Random(20261113).shuffle(records)
        raw = b''.join(encoded(r) for r in records)
        b_path = HERE / f'fixtures/noise-{noise}/B/materials.jsonl'
        c_path = HERE / f'fixtures/noise-{noise}/C/materials.jsonl'
        for path in [b_path, c_path]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        idx, build = build_index(c_path)
        save(c_path.with_name('index.json'), idx)
        scenario = {'unrelated_records': noise, 'auxiliary_records': len(records),
                    'B_C_same_material_sha256': sha(raw), 'C_index_build': build,
                    'storage_bytes': {'A_conclusions': (HERE / 'fixtures/conclusions.json').stat().st_size,
                                      'B_conclusions_plus_materials': (HERE / 'fixtures/conclusions.json').stat().st_size + len(raw),
                                      'C_conclusions_materials_index': (HERE / 'fixtures/conclusions.json').stat().st_size + len(raw) + c_path.with_name('index.json').stat().st_size},
                    'unlimited': {}, 'budgets': []}
        for mode in ['A', 'B', 'C']:
            rows = [{'claim_id': cl['id'], **answer(cl, q, mode, b_path if mode == 'B' else c_path, idx)}
                    for cl, q in zip(conclusions, qs)]
            scenario['unlimited'][mode] = {'summary': summarize(rows, gold), 'answers': rows}
        # A file-only receiver is allowed to organize exactly the same index.
        local_index, local_build = build_index(b_path)
        local_rows = [{'claim_id': cl['id'], **answer(cl, q, 'C', b_path, local_index)}
                      for cl, q in zip(conclusions, qs)]
        scenario['B_builds_once'] = {'build': local_build, 'summary': summarize(local_rows, gold),
                                    'same_index_as_C': local_index == idx}
        for budget in [2, 4, 5, 10, 30, 50, 130]:
            scenario['budgets'].append({'auxiliary_record_budget_per_question': budget, 'conditions': {
                mode: summarize([{'claim_id': cl['id'], **answer(cl, q, mode, b_path if mode == 'B' else c_path,
                                                                idx, budget)} for cl, q in zip(conclusions, qs)], gold)
                for mode in ['A', 'B', 'C']}})
        results['scenarios'].append(scenario)
        if noise == 20:
            # Snapshot verification is a separately charged full-file byte pass, not a free record lookup.
            bad = copy.deepcopy(idx)
            bad['groups']['C05'].remove('C05-observation')
            bad['groups']['C06'].append('C05-observation')
            c5 = answer(conclusions[4], qs[4], 'C', c_path, bad)
            c6 = answer(conclusions[5], qs[5], 'C', c_path, bad)
            reconstructed, refresh = build_index(c_path)
            results['faults'] = {
                'misassigned_relation': {'all_original_files_unchanged': sha(c_path.read_bytes()) == bad['snapshot_sha256'],
                                         'all_ids_still_indexed_once': sorted(sum(bad['groups'].values(), [])) == sorted(idx['entries']),
                                         'C05_verdict': c5, 'C06_verdict': c6,
                                         'gold_C05': gold['C05'], 'fresh_index_differs': reconstructed != bad,
                                         'full_refresh_cost': refresh,
                                         'after_refresh_C05': answer(conclusions[4], qs[4], 'C', c_path, reconstructed)},
                'stale_snapshot': {'changed_snapshot_detected': sha(raw + b'\n') != idx['snapshot_sha256'],
                                   'action': 'stop before indexed lookup; no application verdict',
                                   'verification_bytes': len(raw) + 1},
                'integrity_check_cost': {'read_full_snapshot_bytes_once': len(raw),
                                         'reason': 'hash comparison requires a previously verified snapshot or a byte pass; not charged as zero human work'}}
            # One reuse request, then many repetitions, relative to the cold-scan B policy.
            cl, q = conclusions[5], qs[5]
            b_one = answer(cl, q, 'B', b_path, idx)['cost']
            c_one = answer(cl, q, 'C', c_path, idx)['cost']
            cold_unit = b_one['conclusion_records'] + b_one['evidence_records_read']
            indexed_unit = c_one['conclusion_records'] + c_one['evidence_records_read'] + c_one['index_lookups']
            for write_weight in [0, 1, 5]:
                preparation = build['record_inspections'] + write_weight * build['index_entries_written']
                results['cost_sensitivity'].append({'scope': 'one C06 request repeated; record-read and lookup each1 hypothetical unit',
                    'index_entry_write_weight': write_weight, 'B_cold_per_request': cold_unit,
                    'indexed_per_request': indexed_unit, 'index_preparation': preparation,
                    'first_strict_saving_request': math.floor(preparation / (cold_unit - indexed_unit)) + 1,
                    'B_self_index_and_C_same_cost': True,
                    'full_rebuild_on_update_repeats_preparation': True})
    save(HERE / 'results.json', results)
    return results


if __name__ == '__main__':
    r = run()
    base = r['scenarios'][1]
    print(json.dumps({'noise20': {m: base['unlimited'][m]['summary'] for m in ['A', 'B', 'C']},
                      'break_even': r['cost_sensitivity'],
                      'misassigned_edge_C05': r['faults']['misassigned_relation']['C05_verdict']['status']},
                     ensure_ascii=False, indent=2))
