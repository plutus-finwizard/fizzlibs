import os
import pika
import json
import logging

# TODO: from fizzlibs.ext.qqueue import QQueuePayload, PushQueue
from fizzlibs.ext.handler import AuthHandler


class Deferred_Task_API(AuthHandler):
    def post(self):
        payload = QQueuePayload.unpickle(self.request.body)
        logging.info(payload)

        try:
            payload.handler(*payload.args, **payload.kwargs)
        except Exception as e:
            logging.exception(e)

        return {'message': 'success'}


def defer(func_handler,
          *args,
          _queue='default',
          _countdown=0,
          _target=None,
          **kwargs):
    queue = PushQueue(name=(_queue or 'default'))
    queue.publish(func_handler, *args, **kwargs)
