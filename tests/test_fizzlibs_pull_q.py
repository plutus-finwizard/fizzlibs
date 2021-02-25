import pytest
import logging
import json

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
