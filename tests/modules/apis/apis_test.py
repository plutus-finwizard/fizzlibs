import logging
import json

from fizzlibs.ext.handler import AuthHandler
from fizzlibs.ext import qqueue

class Test_API(AuthHandler):
    def get(self):
        return '200 OK'

    def post(self):
        return self.request.json

class Test_PullQ(AuthHandler):
    def get(self):
        return '200 OK'

    def post(self):
        return '200 OK'

class Test_Pull_Task_API(AuthHandler):
    def get(self):
        q = qqueue.QQueue('default')
        tasks = q.lease_tasks()

        return {
            'message': 'success',
            'data': [json.loads(x) for x in tasks]
        }

    def post(self):
        data = self.request.json
        task = qqueue.Task(json.dumps(data), method='PULL')
        q = qqueue.QQueue('default')
        q.add(task)

        return {'message': 'success'}
