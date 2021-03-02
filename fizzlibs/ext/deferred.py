import os
import pika
import json
import logging
import base64

from fizzlibs.ext import qqueue
from fizzlibs.ext.handler import AuthHandler


class Deferred_Task_API(AuthHandler):
    """
    A class to handle default push route
    ...
    Parameters
    ----------
    Google pubsub request body
    """
    def post(self):
        data = self.request.json
        payload = base64.b64decode(data['message']['data'].encode('utf-8'))

        try:
            task = qqueue.Task.from_pickle(payload)
            task.handler(*task.args, **task.kwargs)
        except Exception as e:
            logging.error(task.handler)
            logging.error(task.args)
            logging.error(task.kwargs)

            raise Exception(e)

        return {'message': 'success'}


def defer(func_handler,
          *args,
          _queue='default',
          _countdown=0,
          _target=None,
          **kwargs):
    """
    Handles push queue
    ...

    Parameters
    ----------
    func_handler : a callable
        To be called upon message received
    *args : arguments
        Positional arguments for callable
    _queue : str
        Name of push queue
    _countdown : int
        Wait before pushing to subscriber

        NOTE: Not implemented
    _target : str
        Specify a different target to push messages

        NOTE: Not implementd
    kwargs : arguments
        Dict arguments for callable
    """

    task = qqueue.Task(handler=func_handler, *args, **kwargs)
    queue = qqueue.QQueue(name=(_queue or 'default'))
    queue.add(task)

    if os.environ.get('FLASK_APP') == 'tests/app:create_app':
        # Required for test automation
        return task.to_pickle().decode('utf-8')
