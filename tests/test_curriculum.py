import copy
import pytest
from coach_app.curriculum import load, validate


def test_complete_curriculum(curriculum):
    modules=curriculum["modules"]
    assert len(modules)==4
    assert sum(len(m["quiz"]) for m in modules)==20
    assert sum(len(m["practice"]) for m in modules)==8
    for m in modules:
        assert len(m["guided"])==2
        assert m["worked"] in m["narration"]
        assert all(q["explanation"] and all(q["feedback"].values()) for q in m["quiz"]+m["practice"])


@pytest.mark.parametrize("fault",["answer","duplicate","feedback","empty","difficulty","concept"])
def test_reject_content_faults(curriculum,fault):
    data=copy.deepcopy(curriculum)
    q=data["modules"][0]["quiz"][0]
    if fault=="answer": q["answer"]="not an option"
    if fault=="duplicate": q["id"]=data["modules"][0]["quiz"][1]["id"]
    if fault=="feedback": q["feedback"]={}
    if fault=="empty": data["modules"][0]["plain"]=""
    if fault=="difficulty": q["difficulty"]=3
    if fault=="concept": q["concept"]="base_rates"
    with pytest.raises(ValueError): validate(data)


def test_malformed_json(tmp_path):
    p=tmp_path/'bad.json'; p.write_text('{broken')
    with pytest.raises(ValueError): load(p)
    with pytest.raises(ValueError): validate({})


def test_answer_key_independent_review(curriculum):
    # Reviewed against the authored arithmetic and interpretation, not generated from q['answer'].
    keys={"expected_value":[1,1,2,2,1,1,2], "independence":[1,2,1,2,1,0,1],
          "conditional_probability":[1,2,1,0,2,1,2], "base_rates":[0,1,2,0,2,1,2]}
    for m in curriculum["modules"]:
        for q,index in zip(m["quiz"]+m["practice"],keys[m["id"]]):
            assert q["answer"]==q["options"][index]
