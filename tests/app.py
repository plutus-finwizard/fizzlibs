import os
import logging
from logging.config import dictConfig

from fizzlibs.ext import webapp
from fizzlibs.ext import vendor

vendor.add('tests/modules')

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def create_app(test_config=None, instance_relative_config=False):
    import apis

    common_routes = apis.api_routes

    # create & configure the app
    app = webapp.FlaskApplication(__name__,
                          common_routes,
                          instance_relative_config=instance_relative_config)

    # app.config.from_yaml('app.yml')

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app
