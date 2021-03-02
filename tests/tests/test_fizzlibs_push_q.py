import pytest
import logging
import json
import time

def test_push_q_post(client):
    response = client.get(f'/api/webapp')

    rtext = response.get_data()

    assert rtext == b'200 OK'
