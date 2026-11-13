"""Finite synthetic counterexample: faithful replay does not establish a correct claim."""
from pathlib import Path
import hashlib
import json


def fingerprint(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def downstream(graph, start):
    seen, queue = set(), [start]
    while queue:
        node = queue.pop(0)
        for child in graph.get(node, []):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return sorted(seen)


def run():
    data = [2, 4, 6]
    # v1 faithfully records a wrong implementation of arithmetic sample mean.
    old = {'version': 'analysis-v1', 'data': data, 'task': 'arithmetic-sample-mean',
           'unit': 'U', 'formula': 'sum/(n-1)', 'reported_result': 6}
    old_hash = fingerprint(old)
    replay = sum(data) / (len(data) - 1)
    intended = sum(data) / len(data)
    new = {'version': 'analysis-v2', 'parent': old['version'], 'data': data,
           'task': old['task'], 'unit': 'U', 'formula': 'sum/n', 'reported_result': intended}
    graph = {'raw-v1': ['analysis-v1', 'count-v1'],
             'analysis-v1': ['mean-claim-v1'], 'mean-claim-v1': ['threshold-decision-v1']}
    affected = downstream(graph, 'analysis-v1')
    independent_check = {'count-v1': len(data)}
    result = {
        'kind': 'synthetic deterministic example; no empirical observations or original-study replication',
        'given_data': data,
        'v1': {'record_sha256': old_hash, 'replay_result': replay,
               'record_integrity': fingerprint(old) == old_hash,
               'matches_recorded_result': replay == old['reported_result'],
               'matches_intended_sample_mean': replay == intended,
               'absolute_error_in_U': abs(replay - intended)},
        'v2': {'parent': new['parent'], 'record_sha256': fingerprint(new),
               'sample_mean': intended, 'old_record_still_unchanged': fingerprint(old) == old_hash},
        'same_given_decision_rule_mean_at_least_5U': {'using_v1': replay >= 5, 'using_v2': intended >= 5},
        'dependency_review': {'changed_node': 'analysis-v1', 'flag_for_review': affected,
                              'not_automatically_false': affected,
                              'independent_count_not_flagged': 'count-v1' not in affected,
                              'independent_count': independent_check['count-v1'],
                              'scope': 'only the explicitly given complete graph; missing dependencies would be missed'},
        'reuse_scope': {'allowed_task': 'arithmetic-sample-mean', 'new_task': 'population-forecast',
                        'automatically_authorized': False,
                        'reason': 'a correct sample statistic alone does not validate a new population forecast'},
        'limitations': ['The decision threshold5U and dependency graph are stipulated, not normative or empirically estimated.',
                        'An immutable digest identifies retained content; it does not establish the truth of observations.',
                        'The graph flags possible impact, not the truth value of downstream claims.',
                        'Independent review, complete traceability and maintenance have costs not estimated here.']
    }
    return result


if __name__ == '__main__':
    p = Path(__file__).with_name('example-results.json')
    results = run()
    p.write_bytes((json.dumps(results, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'v1': results['v1'], 'v2': results['v2'],
                      'review': results['dependency_review']['flag_for_review']}, indent=2))
