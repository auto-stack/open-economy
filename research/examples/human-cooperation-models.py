"""Two illustrative conditional results, not evolutionary simulations or human data."""
from fractions import Fraction as F
from pathlib import Path
import json


def repeated_donation(b, c, delta):
    # Perfect observation, infinite discounted horizon; both use grim trigger.
    # A unilateral defector gains c now and loses b-c in every later period.
    if not (b > c > 0 and 0 <= delta < 1):
        raise ValueError('Require b>c>0 and 0<=delta<1')
    cooperate = (b-c)/(1-delta)
    defect_once = b
    return cooperate, defect_once


def public_good(contributions, punishments=()):
    # Each tuple is (punisher, target, points); punishment rules are exogenous.
    n, endowment, mpcr = 4, F(20), F(2, 5)
    if len(contributions) != n or any(not 0 <= x <= endowment for x in contributions):
        raise ValueError('Four contributions in [0,20] required')
    payoff = [endowment-x+mpcr*sum(contributions) for x in contributions]
    points_total = F(0)
    for i, j, points in punishments:
        if i == j or not (0 <= i < n and 0 <= j < n and 0 <= points <= 10):
            raise ValueError('Invalid punishment')
        payoff[i] -= points
        payoff[j] -= 3*points
        points_total += points
    # Direct resource accounting; fines are destroyed, not transferred.
    expected_total = n*endowment+(n*mpcr-1)*sum(contributions)-4*points_total
    assert sum(payoff) == expected_total
    return {'payoffs':[str(x) for x in payoff], 'total':str(sum(payoff)),
            'max_minus_min':str(max(payoff)-min(payoff))}


def main():
    checks = 0
    # Independent incentive inequality versus continuation-value comparison.
    for b, c in [(F(3),F(1)),(F(5),F(2)),(F(7),F(3))]:
        for delta in [F(0), F(1,5), c/b, F(1,2), F(4,5), F(99,100)]:
            v, deviation = repeated_donation(b,c,delta)
            assert (v >= deviation) == (delta >= c/b)
            checks += 1
    repeated = []
    for delta in [F(1,5),F(1,3),F(4,5)]:
        v, dev = repeated_donation(F(3),F(1),delta)
        repeated.append({'b':3,'c':1,'delta':str(delta),'cooperation_value':str(v),
                         'one_deviation_value':str(dev),'no_profitable_deviation':v>=dev})
    public = {
        'all_zero':public_good([F(0)]*4),
        'all_twenty':public_good([F(20)]*4),
        'three_contribute':public_good([F(20),F(20),F(20),F(0)]),
        'one_point_to_defector':public_good([F(20),F(20),F(20),F(0)],[(0,3,F(1))]),
        'one_point_to_cooperator':public_good([F(20),F(20),F(20),F(0)],[(3,0,F(1))]),
    }
    assert public['all_twenty']['total']=='128'
    assert public['all_zero']['total']=='80'
    assert public['three_contribute']['total']=='116'
    assert public['one_point_to_defector']['total']=='112'
    assert public['one_point_to_cooperator']['total']=='112'
    # Maximum private gain from withholding 20 is (1-.4)*20=12.
    deviation_gain=(1-F(2,5))*20
    assert deviation_gain==12 and F(3)<deviation_gain
    result={'research_date_local':'2026-11-12','status':'illustrative algebra and accounting; no empirical fit',
            'repeated_donation':repeated,'public_good':public,
            'private_gain_from_withholding_twenty':str(deviation_gain),
            'verification':{'discount_comparisons':checks,'public_good_scenarios':len(public)}}
    path=Path(__file__).with_name('human-cooperation-results.json')
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
