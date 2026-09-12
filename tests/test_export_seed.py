import json
from coach_app.seed_demo import seed


def test_synthetic_records_are_idempotent_and_explicit(tmp_path):
    first=seed(tmp_path/'synthetic.sqlite3')
    again=seed(tmp_path/'synthetic.sqlite3')
    assert first==again
    assert first['session']['synthetic']==1
    assert first['coach_metrics']==[]
    assert first['attempts']==[]
    assert len(first['events'])==2
    assert json.loads(json.dumps(first))==first
