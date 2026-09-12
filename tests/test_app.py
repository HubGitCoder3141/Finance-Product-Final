"""User journeys through real Streamlit widgets with isolated temporary storage."""

import json
import pytest
from streamlit.testing.v1 import AppTest
from coach_app.curriculum import load
from coach_app.storage import Repository


def button(app, label):
    return next(b for b in app.button if b.label==label)


def radio(app,label):
    return next(r for r in app.radio if r.label==label)


def healthy(app):
    assert not app.exception
    assert not app.error


@pytest.fixture
def app(tmp_path,monkeypatch):
    monkeypatch.setenv('COACH_DB_PATH',str(tmp_path/'app.sqlite3'))
    monkeypatch.delenv('ANTHROPIC_API_KEY',raising=False)
    return AppTest.from_file('streamlit_app.py',default_timeout=10).run()


@pytest.mark.parametrize('mid',['expected_value','independence','conditional_probability','base_rates'])
def test_module_full_quiz_practice_journey(app,mid):
    modules=load()['modules']; m=next(m for m in modules if m['id']==mid)
    app.button(key=f'nav_{mid}').click().run(); healthy(app)
    radio(app,'Lesson section').set_value('Equation').run(); healthy(app)
    assert len(app.latex)==1
    radio(app,'Lesson section').set_value('Examples').run()
    for i,step in enumerate(m['guided']):
        radio(app,step['prompt']).set_value(step['answer']).run()
        button(app,f'Check step {i+1}').click().run()
    assert len(app.success)>=2
    radio(app,'Lesson section').set_value('Quiz').run()
    # No answer: validate without scoring.
    button(app,'Submit answer').click().run()
    assert app.warning
    for i,q in enumerate(m['quiz']):
        if i==0:
            button(app,'Show hint').click().run()
            assert any('Assistance used' in x.value for x in app.info)
        choice=q['answer'] if i!=1 else next(o for o in q['options'] if o!=q['answer'])
        radio(app,'Choose one answer').set_value(choice).run()
        button(app,'Submit answer').click().run(); healthy(app)
        if i<4: button(app,'Next question').click().run()
    assert {m.label:m.value for m in app.metric}=={'Unassisted correct':'3','Assisted correct':'1','Incorrect':'1'}
    button(app,'Continue with additional practice').click().run()
    for i,q in enumerate(m['practice']):
        radio(app,'Choose one answer').set_value(q['answer']).run()
        button(app,'Submit answer').click().run()
        if i==0: button(app,'Next question').click().run()
    assert any('every available practice question' in x.value for x in app.success)
    radio(app,'Lesson section').set_value('Quiz').run()
    button(app,'Start a fresh quiz attempt').click().run(); healthy(app)
    assert radio(app,'Choose one answer').value is None
    assert not any('Assistance used' in x.value for x in app.info)


def test_coach_assists_active_question_and_reset(app,monkeypatch):
    radio(app,'Lesson section').set_value('Quiz').run()
    button(app,'Ask a Question about this question').click().run()
    app.text_area(key='message_expected_value').set_value('explain this concept')
    button(app,'Send to demo coach').click().run(); healthy(app)
    assert any('Scripted demo hint' in t.value for t in app.text)
    assert any('Assistance used' in x.value for x in app.info)
    q=load()['modules'][0]['quiz'][0]
    radio(app,'Choose one answer').set_value(q['answer']).run()
    button(app,'Submit answer').click().run()
    button(app,'Reset this conversation').click().run()
    assert app.session_state['histories']['expected_value']==[]
    # Conversation reset leaves assistance and metrics intact.
    button(app,'Progress & measurements').click().run(); healthy(app)
    metrics={m.label:m.value for m in app.metric}
    assert metrics['Assisted correct']=='1' and metrics['Local responses']=='1'
    assert len(app.get('download_button'))==1
    old=app.session_state['session_id']
    app.checkbox(key='confirm_reset').check().run()
    app.button(key='reset_progress').click().run(); healthy(app)
    assert app.session_state['session_id']!=old
    assert app.session_state['page']=='expected_value'


def test_navigation_preserves_quiz_choice_and_events(app):
    radio(app,'Lesson section').set_value('Quiz').run()
    q=load()['modules'][0]['quiz'][0]
    radio(app,'Choose one answer').set_value(q['answer']).run()
    button(app,'Home · learning path').click().run()
    app.text_input(key='search_lessons').set_value('nothing-matches').run()
    assert any('No matching' in i.value for i in app.info)
    app.button(key='nav_expected_value').click().run()
    radio(app,'Lesson section').set_value('Quiz').run()
    assert radio(app,'Choose one answer').value==q['answer']
    healthy(app)


def test_interactives_and_invalid_total(app):
    app.number_input(key='ev_p0').set_value(.4).run()
    button(app,'Calculate weighted average').click().run()
    assert any('must total 1' in w.value for w in app.warning)
    app.number_input(key='ev_p10').set_value(.6).run()
    button(app,'Calculate weighted average').click().run()
    assert app.metric[0].value=='6.00 minutes'
    app.button(key='nav_independence').click().run()
    app.toggle(key='ind_replace').set_value(False).run()
    button(app,'Record this comparison').click().run(); healthy(app)
    app.button(key='nav_conditional_probability').click().run()
    radio(app,'Count within').set_value('Music members').run()
    button(app,'Record this sample space').click().run()
    assert app.metric[0].value=='6/18 = 33.33%'
    app.button(key='nav_base_rates').click().run()
    app.slider(key='base_prevalence').set_value(10).run()
    button(app,'Record this population').click().run()
    assert app.metric[0].value=='50.00%'
    healthy(app)


def test_nonquiz_coach_supported_fallback_and_limits(app):
    for message,part in [('explain expected value','Scripted demo:'),('flibbertigibbet','cannot interpret arbitrary')]:
        # Let AppTest consume the previous form trigger, as the browser does.
        app.run()
        app.session_state['last_send']=-1000
        app.text_area(key='message_expected_value').set_value(message)
        button(app,'Send to demo coach').click().run(); healthy(app)
        assert any(part in t.value for t in app.text)
    app.run()
    app.session_state['coach_count']=80
    app.text_area(key='message_expected_value').set_value('why')
    button(app,'Send to demo coach').click().run()
    assert any('80 demo responses' in w.value for w in app.warning)


def test_app_sessions_are_distinct(app):
    second=AppTest.from_file('streamlit_app.py').run()
    healthy(second)
    assert second.session_state['session_id']!=app.session_state['session_id']


def test_unexpected_render_failure_is_safe(app,monkeypatch):
    def broken(*args,**kwargs):
        raise RuntimeError('private-configuration-value')
    monkeypatch.setattr('coach_app.pages.render_interactive',broken)
    app.run()
    assert not app.exception
    assert len(app.error)==1
    assert 'private-configuration-value' not in app.error[0].value
