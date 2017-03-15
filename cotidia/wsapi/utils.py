from channels.handler import AsgiRequest

from django.urls import reverse, resolve
from django.http import HttpRequest
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import AnonymousUser

from django.utils.six.moves.urllib.parse import urlencode

from io import BytesIO


class RequestFactory(object):
    def __init__(self, action, path, data={}, user=None):
        self.action = action
        self.path = path
        self.encoded_data = urlencode(data)
        self.user = user

    def build_request(self, environ):
        req = WSGIRequest(environ)
        self.auth_request(req)
        return req

    def auth_request(self, req):
        if self.user:
            req.user = self.user
        else:
            req.user = AnonymousUser()
        return req

    def get(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': self.path,
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(self.encoded_data),
            'wsgi.input': BytesIO(self.encoded_data.encode())
            }
        return self.build_request(environ)

    def post(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': self.path,
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(self.encoded_data),
            'wsgi.input': BytesIO(self.encoded_data.encode())
            }
        return self.build_request(environ)

    def patch(self):
        environ = {
            'REQUEST_METHOD': 'PATCH',
            'PATH_INFO': self.path,
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(self.encoded_data),
            'wsgi.input': BytesIO(self.encoded_data.encode())
            }
        return self.build_request(environ)

    def request(self):
        if self.action == "get":
            return self.get()
        elif self.action in ["create", "replace"]:
            return self.post()
        elif self.action == "update":
            return self.patch()


class WSAPIAdapter(object):

    def __init__(self, get_url_args, message):
        self.get_url_args = get_url_args or self._get_url_args
        self.message = message
        self.action = self.message["action"]

    def _get_url_args(self, message):
        url_name = "{entity}-{action}".format(
            entity=message["entity"],
            action=message["action"],
            )
        url_parameters = {}
        if message["meta"].get("uuid"):
            url_parameters["uuid"] = message["meta"]["uuid"]
        return url_name, url_parameters

    def resolve(self):
        route_name, url_params = self.get_url_args(self.message)
        path = reverse(route_name, kwargs=url_params)
        func, args, kwargs = resolve(path)
        return path, func, args, kwargs

    def message_to_request(self):
        path, func, args, kwargs = self.resolve()
        data = self.message.get("data", {})
        user = None
        request = RequestFactory(self.action, path, data, user).request()
        response = func(request, *args, **kwargs)

        payload = self.process_response(response.data)

        return payload

    def process_response(self, data):
        new_data = data

        return new_data

        # print("URL name", url_name)
        #
        # request = AsgiRequest(self.message)
        # # print(request)
        # print("Message to process", message.http_session)
        #
        # if message['action'] == 'store':
        #     if message['entity'] == 'job':
        #         route = 'callsheet.api.update'
        #
        #
        # # we have a route
        # view = reverse(route, {message['meta']})
        #
        # return view(message[data])
