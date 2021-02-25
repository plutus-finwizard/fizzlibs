from flask import request, make_response
from flask.views import MethodView


class RequestObject(object):
    @property
    def headers(self):
        return request.headers

    @property
    def body(self):
        return request.get_data()

    @property
    def params(self):
        return request.args

    @property
    def files(self):
        return request.files

    @property
    def form(self):
        return request.form

    @property
    def json(self):
        return request.get_json()

    def get(self, name):
        return request.values.get(name)


class AuthHandler(MethodView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = RequestObject()
        self.response = make_response()
