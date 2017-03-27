import json

from io import BytesIO

from django.urls import reverse, resolve
from django.core.handlers.wsgi import WSGIRequest
from django.utils.six.moves.urllib.parse import urlencode


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
