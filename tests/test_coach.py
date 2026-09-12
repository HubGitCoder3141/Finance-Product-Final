import json
import socket
from unittest.mock import patch
import pytest
from coach_app.coach import HINTS, PlaceholderCoach
from coach_app.curriculum import DATA_DIR
from coach_app.evaluate import evaluate
from coach_app.instrumentation import measured_reply, measurement_summary


def test_evaluation_cases_without_network(monkeypatch):
    def fail(*args,**kwargs): raise AssertionError('Unexpected network request')
    monkeypatch.setattr(socket.socket,'connect',fail)
    monkeypatch.setattr(socket,'create_connection',fail)
    monkeypatch.setenv('ANTHROPIC_API_KEY','dummy-present-but-unused')
    monkeypatch.setenv('COACH_PROVIDER','live')
    report=evaluate()
    assert len(report['results'])==14
    assert all(r['passed'] for r in report['results'])
    assert report['api_requests']==0


def test_quiz_context_always_scaffolds():
    service=PlaceholderCoach()
    for module in HINTS:
        for message in ['explain this concept','banana','why?']:
            reply=service.respond(message,module,True)
            assert reply.route=='hint'
            assert reply.text=='Scripted demo hint: '+HINTS[module]


@pytest.mark.parametrize('message',['','   ','x'*1001])
def test_message_validation(message):
    with pytest.raises(ValueError): PlaceholderCoach().respond(message,'expected_value')


def test_instrumentation_actual_time_no_text(repo):
    with patch('coach_app.instrumentation.perf_counter',side_effect=[10,10.025]):
        measured_reply(PlaceholderCoach(),repo,'learner-a','expected_value','explain secret-personal-text')
    data=repo.export('learner-a'); m=data['coach_metrics'][0]
    assert m['elapsed_ms']==pytest.approx(25)
    assert m['provider_mode']=='placeholder'
    assert m['api_cost_usd']==0 and m['api_requests']==0
    assert m['input_tokens'] is None and m['output_tokens'] is None
    assert 'secret-personal-text' not in json.dumps(data)
    assert measurement_summary(data)['mean_local_ms']==pytest.approx(25)
    assert measurement_summary(repo.export('learner-b'))['mean_local_ms'] is None


def test_sanitized_error_event(repo):
    with pytest.raises(ValueError): measured_reply(PlaceholderCoach(),repo,'learner-a','expected_value','')
    data=repo.export('learner-a')
    assert data['events'][0]['detail']=={'code':'coach_response_failed'}
    assert data['coach_metrics']==[]


def test_provenance_and_boundary_coverage():
    cases=json.loads((DATA_DIR/'evaluation_cases.json').read_text(encoding='utf-8'))['cases']
    assert sum(c['expected_route']=='answer_redirect' for c in cases)>=2
    assert sum(c['expected_route']=='betting_redirect' for c in cases)>=1
    for c in cases:
        assert all(c[k] for k in ('concept','learner_says','misconception','good_response','provenance'))
        assert c['provenance']['quotation'] is False
