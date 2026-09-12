import math
import pytest
from coach_app.math_logic import conditional, expected_value, frequencies, from_counts, independent, probability, second_blue


def test_verified_examples():
    assert expected_value([0,10],[.5,.5]) == 5
    assert expected_value([2,6],[.75,.25]) == 3
    assert expected_value([1,4],[.2,.8]) == pytest.approx(3.4)
    assert expected_value([1,2,3,4,5,6],[1/6]*6) == pytest.approx(3.5)
    assert expected_value([-2,2],[.5,.5]) == 0
    assert second_blue(3,10,True) == .3
    assert second_blue(3,10,False) == 2/9
    assert from_counts(6,18,30) == 1/3
    assert from_counts(6,12,30) == .5
    assert conditional(.12,.3) == .4
    assert independent(.5,.4,.2)
    assert not independent(.5,.4,.1)
    assert frequencies(1000,.02,.9,.1)["posterior"] == pytest.approx(18/116)
    assert frequencies(1000,.1,.9,.1)["posterior"] == pytest.approx(.5)


@pytest.mark.parametrize("p",[-.1,1.1,math.nan,math.inf,True,"0.5",None])
def test_probability_rejects_bad_values(p):
    with pytest.raises(ValueError): probability(p)


@pytest.mark.parametrize("xs,ps",[([],[]),([1],[.4,.6]),([1,2],[.4,.4]),([1,2],[-.1,1.1]),([math.inf],[1])])
def test_invalid_distributions(xs,ps):
    with pytest.raises(ValueError): expected_value(xs,ps)


@pytest.mark.parametrize("fn,args",[(conditional,(0,0)),(conditional,(.5,.2)),(from_counts,(3,2,4)),(from_counts,(1,3,2)),(from_counts,(0,0,0)),(from_counts,(1.5,2,3)),(second_blue,(0,10,False)),(second_blue,(3,2,True)),(independent,(.9,.9,.1)),(frequencies,(0,.1,.9,.1))])
def test_count_and_joint_edge_cases(fn,args):
    with pytest.raises(ValueError): fn(*args)


def test_base_rate_boundaries():
    assert frequencies(1000,.5,0,0)["posterior"] is None
    assert frequencies(1000,0,.9,.1)["posterior"] == 0
    assert frequencies(1000,1,.9,.1)["posterior"] == 1
    low_false = frequencies(1000,.02,.9,.01)["posterior"]
    high_false = frequencies(1000,.02,.9,.1)["posterior"]
    assert low_false > high_false
