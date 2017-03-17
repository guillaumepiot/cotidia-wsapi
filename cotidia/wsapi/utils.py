import json

from django.urls import reverse, resolve
from django.core.handlers.wsgi import WSGIRequest
from django.utils.six.moves.urllib.parse import urlencode

from rest_framework.authtoken.models import Token

from io import BytesIO


class RequestFactory(object):
    def __init__(self, action, path, data={}, auth_token=None):
        self.action = action
        self.path = path
        self.encoded_data = urlencode(data)
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
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(self.encoded_data),
            'wsgi.input': BytesIO(self.encoded_data.encode())
            })
        return self.build_request(environ)

    def post(self):
        environ = self.get_base_environ()
        environ.update({
            'REQUEST_METHOD': "POST",
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(self.encoded_data),
            'wsgi.input': BytesIO(self.encoded_data.encode())
            })
        return self.build_request(environ)

    def patch(self):
        environ = self.get_base_environ()
        environ.update({
            'REQUEST_METHOD': "PATCH",
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(self.encoded_data),
            'wsgi.input': BytesIO(self.encoded_data.encode())
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
        elif self.action in ["create", "replace"]:
            return self.post()
        elif self.action == "update":
            return self.patch()
        elif self.action == "delete":
            return self.delete()


class WSAPIAdapter(object):

    def __init__(self, message, get_url_args):
        self.get_url_args = get_url_args or self._get_url_args
        self.message = message
        self.content = json.loads(message.content["text"])

    def _get_url_args(self, message):
        action = message["action"]

        if action in ["update", "replace"]:
            url_action = "update"
        else:
            url_action = action

        url_name = "{entity}-{action}".format(
            entity=message["entity"],
            action=url_action,
            )
        url_parameters = {}
        if message["meta"].get("uuid"):
            url_parameters["uuid"] = message["meta"]["uuid"]
        return url_name, url_parameters

    def resolve(self):
        route_name, url_params = self.get_url_args(self.content)
        path = reverse(route_name, kwargs=url_params)
        func, args, kwargs = resolve(path)
        return path, func, args, kwargs

    def message_to_request(self):
        path, func, args, kwargs = self.resolve()
        data = self.content.get("data", {})
        auth_token = self.message.auth_token
        request = RequestFactory(
            self.content["action"], path, data, auth_token
            ).request()
        response = func(request, *args, **kwargs)

        payload = self.process_response(response.data)

        return payload

    def get_response_action(self):
        action = self.content.get("action")
        if action in ["get", "list", "create", "replace", "update"]:
            return "store"
        elif action == "delete":
            return "delete"
        else:
            return None

    def process_response(self, data):
        new_data = {
            "action": self.get_response_action(),
            "entity": self.content.get("entity")
        }

        if self.content.get("meta"):
            new_data["meta"] = self.content["meta"]

        if self.content.get("action") == "create":
            if not new_data.get("meta"):
                new_data["meta"] = {}
            new_data["meta"]["uuid"] = data.get("uuid")

        if data:
            new_data["data"] = data

        return new_data
