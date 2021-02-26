import os
import yaml
import logging

from flask import Flask
from flask import Config
# from flask import request


class FlaskConfig(Config):
    def from_yaml(self, config_file):
        env = os.environ.get('FLASK_ENV', 'development')
        self['ENVIRONMENT'] = env.lower()

        with open(os.path.join(self.root_path, config_file)) as f:
            c = yaml.load(f)

        c = c.get(env, c)

        for key in c.keys():
            if key.isupper():
                self[key] = c[key]


class FlaskApplication(Flask):
    def __init__(self, name, routes, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        self._add_api_routes(routes)
        self._add_deferred_route()

        self.__load_queue()

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path

        return FlaskConfig(root_path, self.default_config)

    def __load_queue(self):
        from fizzlibs.ext import qqueue
        logging.info('Sync: loading queue configurations')

        queue_conf_yaml_path = os.path.join(self.root_path, 'queue.yaml')

        if not os.path.isfile(queue_conf_yaml_path):
            return

        with open(queue_conf_yaml_path) as f:
            queues_conf = yaml.load(f)

        queues = queues_conf.get('queue')

        for queue in queues:
            qqueue.QQueue(**queue, initialize_queue=True)

    def _add_api_routes(self, routes):
        api_id = 1

        for route in routes:
            self.add_url_rule(
                route.rule,
                view_func=route.handler.as_view(f'{route.name}_{api_id}'))
            api_id += 1

    def _add_deferred_route(self):
        from fizzlibs.ext.deferred import Deferred_Task_API

        self.add_url_rule('/_ah/queue/deferred',
                          view_func=Deferred_Task_API.as_view('deferred'))


class Route():
    def __init__(self, rule, handler):
        self.rule = rule
        self.name = handler.__name__
        self.handler = handler
