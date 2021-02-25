from .apis_test import *

from fizzlibs.ext import webapp

api_routes = [
    webapp.Route('/api/webapp', handler=Test_API),
    webapp.Route('/api/tasks/pull', handler=Test_Pull_Task_API)
]
