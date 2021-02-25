import pytest
import logging
import json

def test_webapp_get(client):
    response = client.get(f'/api/webapp')

    rtext = response.get_data()

    assert rtext == b'200 OK'

def test_webapp_post(client):
    response = client.post(
        f'/api/webapp',
        data=json.dumps({'a': 1, 'b': 2}),
        content_type='application/json'
    )

    data = response.get_json()

    assert data['a'] == 1
    assert data['b'] == 2
