"""Four stipulated histories with the same endpoint; no empirical calibration."""
from collections import Counter
from pathlib import Path
import json


def construct():
    start = {f'p{i}': 'A' if i < 4 else 'B' for i in range(8)}
    histories = []
    for mechanism in ['individual_trial', 'social_learning']:
        end = dict(start)
        events = []
        for person in ['p4', 'p5']:
            end[person] = 'A'
            events.append({'person': person, 'from': 'B', 'to': 'A',
                           'information_source': 'own_trial' if mechanism == 'individual_trial' else 'observed_p0'})
        histories.append({'mechanism': mechanism, 'end': end, 'events': events})
    end = {p: t for p, t in start.items() if p not in ['p4', 'p5']}
    end.update({'entrant0': 'A', 'entrant1': 'A'})
    histories.append({'mechanism': 'membership_turnover', 'end': end,
                      'events': {'exits': ['p4', 'p5'], 'entrants': ['entrant0', 'entrant1']}})
    contribution = [2, 2, 1, 1, 1, 1, 0, 0]
    end, lineage = {}, []
    for parent, n in zip(start, contribution):
        for k in range(n):
            child = f'child_{parent}_{k}'
            end[child] = start[parent]
            lineage.append({'parent': parent, 'child': child, 'type': start[parent]})
    histories.append({'mechanism': 'biological_generation_stipulated_faithful_transmission',
                      'end': end, 'events': lineage})
    for h in histories:
        h['end_counts'] = dict(Counter(h['end'].values()))
        h['retained_actor_ids'] = len(set(start) & set(h['end']))
        assert h['end_counts'] == {'A': 6, 'B': 2}
    return {'status': 'constructed_identification_counterexample_not_empirical',
            'start': start, 'start_counts': dict(Counter(start.values())), 'histories': histories,
            'limitations': ['No performance ordering A>B assumed.',
                            'Biological faithful transmission is stipulated, not a claim about learned skills.',
                            'Within-agent learning and between-agent transmission can overlap.']}


if __name__ == '__main__':
    result = construct()
    Path(__file__).with_name('example-results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('4 constructed histories; all endpoints 6A/2B; no empirical parameters.')
