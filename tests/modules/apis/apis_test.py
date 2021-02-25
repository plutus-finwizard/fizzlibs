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

        q.delete_tasks(tasks)

        return {
            'message': 'success',
            'data': [json.loads(x.payload) for x in tasks]
        }

    def post(self):
        data = self.request.json
        task = qqueue.Task(payload=json.dumps(data), method='PULL')

        q = qqueue.QQueue('default')
        ack_id = q.add(task)

        return {'message': 'success', 'ack_id': ack_id}
