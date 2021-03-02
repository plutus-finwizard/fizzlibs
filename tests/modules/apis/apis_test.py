import logging
import json

from fizzlibs.ext.handler import AuthHandler
from fizzlibs.ext import qqueue
from fizzlibs.ext import deferred

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

        if tasks:
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

class Test_Pull_Multiple_Task_API(AuthHandler):
    def get(self):
        q = qqueue.QQueue('default')
        tasks = q.lease_tasks()

        delete = self.request.get('delete', 'True')

        if delete == 'True' and tasks:
            q.delete_tasks(tasks)

        return {
            'message': 'success',
            'data': [json.loads(x.payload) for x in tasks],
            'tasks': [x.to_pickle().decode('utf-8') for x in tasks]
        }

    def post(self):
        data = self.request.json
        tasks = [qqueue.Task(payload=json.dumps(q), method='PULL') for q in data['tasks']]

        q = qqueue.QQueue('default')
        ack_ids = q.add(tasks)

        return {'message': 'success', 'ack_ids': ack_ids}

    def put(self):
        data = self.request.json
        logging.info (data)
        tasks = [qqueue.Task.from_pickle(x.encode('utf-8')) for x in data]

        logging.error(tasks)

        q = qqueue.QQueue('default')
        q.modify_task_lease(tasks, lease_seconds=0)

        return {'message': 'success'}

def call_deferred_func(title, name):
    logging.info (f'{title}, {name}')

class Test_Push_Q_API(AuthHandler):
    def get(self):
        b64 = deferred.defer(call_deferred_func, '19', 'covid')
        return b64
