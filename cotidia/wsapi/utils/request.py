from io import BytesIO

from django.core.handlers.wsgi import WSGIRequest
from rest_framework.renderers import JSONRenderer


class RequestFactory(object):
    def __init__(self, action, path, data={}, auth_token=None):
        self.action = action
        self.path = path
        self.data = JSONRenderer().render(data)
        self.auth_token = auth_token

    def build_request(self, environ):
        req = WSGIRequest(environ)
        return req

    def get_base_environ(self):
        environ = {
            'PATH_INFO': self.path,
        }
        if self.auth_token:
            environ["HTTP_AUTHORIZATION"] = 'Token %s' % self.auth_token
        return environ

    def get(self):
        environ = self.get_base_environ()
        environ.update({
            'REQUEST_METHOD': "GET",
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': len(self.data),
            'wsgi.input': BytesIO(self.data)
            })
        return self.build_request(environ)

    def post(self):
        environ = self.get_base_environ()
        environ.update({
            'REQUEST_METHOD': "POST",
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': len(self.data),
            'wsgi.input': BytesIO(self.data)
            })
        return self.build_request(environ)

    def patch(self):
        environ = self.get_base_environ()
        environ.update({
            'REQUEST_METHOD': "PATCH",
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': len(self.data),
            'wsgi.input': BytesIO(self.data)
            })
        return self.build_request(environ)

    def delete(self):
        environ = self.get_base_environ()
        environ.update({
            'REQUEST_METHOD': "DELETE",
            'wsgi.input': BytesIO()
            })
        return self.build_request(environ)

    def request(self):
        if self.action == "list":
            return self.get()
        elif self.action == "get":
            return self.get()
        elif self.action in ["create", "replace", "copy"]:
            return self.post()
        elif self.action == "update":
            return self.patch()
        elif self.action == "delete":
            return self.delete()
