import json
import pytest
from coach_app.quiz import completed, score, summarize
from coach_app.storage import Repository


def test_scoring_assisted_and_wrong(curriculum):
    q=curriculum["modules"][0]["quiz"][0]
    a=score(q,q["answer"],False).to_dict()
    b=score(q,q["answer"],True).to_dict()
    c=score(q,q["options"][0],True).to_dict()
    assert summarize([a,b,c])==dict(unassisted_correct=1,assisted_correct=1,incorrect=1,answered=3)
    with pytest.raises(ValueError): score(q,"",False)


def test_duplicate_retry_assistance_and_persistence(repo,curriculum):
    q=curriculum["modules"][0]["quiz"][0]
    run=repo.current_run('learner-a','expected_value')
    repo.mark_assisted('learner-a',run,q['id'])
    first=repo.submit('learner-a',run,q,q['answer'])
    assert first['correct']==1 and first['assisted']==1
    assert repo.submit('learner-a',run,q,q['options'][0])==first
    assert len(repo.attempts('learner-a',run))==1
    other=Repository(repo.path)
    assert other.current_run('learner-a','expected_value')==run
    assert other.attempts('learner-a',run)==[first]
    fresh=repo.new_run('learner-a','expected_value')
    assert fresh!=run and repo.attempts('learner-a',fresh)==[]
    assert not repo.is_assisted('learner-a',fresh,q['id'])
    assert repo.submit('learner-a',fresh,q,q['answer'])['assisted']==0


def test_session_separation_reset_export(repo,curriculum):
    q=curriculum['modules'][0]['quiz'][0]
    run=repo.current_run('learner-a','expected_value')
    repo.submit('learner-a',run,q,q['answer'])
    repo.event('learner-a','section_visited','expected_value',dedupe='visit')
    repo.event('learner-a','section_visited','expected_value',dedupe='visit')
    repo.event('learner-b','section_visited','base_rates')
    with pytest.raises(ValueError): repo.attempts('learner-b',run)
    with pytest.raises(ValueError): repo.submit('learner-b',run,q,q['answer'])
    with pytest.raises(ValueError): repo.mark_assisted('learner-b',run,q['id'])
    a=repo.export('learner-a'); b=repo.export('learner-b')
    assert len(a['events'])==1 and len(b['attempts'])==0
    assert json.loads(json.dumps(a))==a
    repo.reset('learner-a')
    assert repo.export('learner-b')==b
    with pytest.raises(ValueError): repo.export('learner-a')


def test_all_questions_required_for_completion(repo,curriculum):
    qs=curriculum['modules'][0]['quiz']
    run=repo.current_run('learner-a','expected_value')
    ids=[q['id'] for q in qs]
    for q in qs[:-1]: repo.submit('learner-a',run,q,q['options'][0])
    assert not completed(ids,repo.attempts('learner-a',run))
    repo.submit('learner-a',run,qs[-1],qs[-1]['options'][0])
    assert completed(ids,repo.attempts('learner-a',run))


def test_sql_parameterization(repo):
    value="x'); DROP TABLE sessions; --"
    repo.event('learner-a','test',detail={'safe_data':value})
    assert repo.export('learner-a')['events'][0]['detail']['safe_data']==value
