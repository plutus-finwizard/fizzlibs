import pytest
import logging
import json

@pytest.fixture
def cached():
    class Cached(object):
        def __init__(self):
            self.tasks = None

    return Cached()

@pytest.fixture
def step_data():
    return {}

def test_pull_q_post(client):
    response = client.post(
        f'/api/tasks/pull',
        data=json.dumps({'tasks': 'A huge task'}),
        content_type='application/json'
    )

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'
    assert data['ack_id'] is not None

def test_pull_q_message(client):
    response = client.get(f'/api/tasks/pull')

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'
    assert data['data'][0]['tasks'] == 'A huge task'

def test_pull_q_message_empty(client):
    response = client.get(f'/api/tasks/pull')

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'
    assert data['data'] == []

def test_pull_q_post_multi(client):
    response = client.post(
        f'/api/tasks/pull/multiple',
        data=json.dumps({'tasks': [{'a': 'A huge task'}, {'a': 'A huge task'}]}),
        content_type='application/json'
    )

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'
    assert data['ack_ids'] is not []

def test_pull_q_message_multi(client):
    response = client.get(f'/api/tasks/pull/multiple')

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'

    for task in data['data']:
        assert task['a'] == 'A huge task'

def test_pull_q_message_empty(client):
    response = client.get(f'/api/tasks/pull/multiple')

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'
    assert data['data'] == []


def test_pull_q_post_requeue(client):
    response = client.post(
        f'/api/tasks/pull/multiple',
        data=json.dumps({'tasks': [{'b': 'A huge task'}, {'b': 'A huge task'}]}),
        content_type='application/json'
    )

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'
    assert data['ack_ids'] is not []

def test_pull_q_message_requeue(client, request):
    response = client.get(f'/api/tasks/pull/multiple?delete=False')

    data = response.get_json()

    assert data['message'] == 'success'

    for task in data['data']:
        assert task['b'] == 'A huge task'

    request.config.cache.set('shared', data['tasks'])

# TODO: verify with application
# def test_pull_q_message_empty_verify(client, request):
#     response = client.get(f'/api/tasks/pull/multiple')

#     data = response.get_json()

#     logging.info (data)

#     assert data['message'] == 'success'
#     assert data['data'] == []

def test_pull_q_message_empty_requeue(client, request):
    response = client.put(
        f'/api/tasks/pull/multiple',
        data=json.dumps(request.config.cache.get('shared', None)),
        content_type='application/json'
    )

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'

def test_pull_q_message_requeue(client):
    response = client.get(f'/api/tasks/pull/multiple')

    data = response.get_json()

    logging.info (data)

    assert data['message'] == 'success'

    for task in data['data']:
        assert task['b'] == 'A huge task'
