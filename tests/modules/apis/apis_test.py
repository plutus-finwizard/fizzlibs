import logging
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
    def post(self):


