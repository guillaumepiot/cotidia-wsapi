import json

from django.urls import reverse, resolve, get_resolver
from rest_framework.renderers import JSONRenderer

from cotidia.wsapi.utils.request import RequestFactory


class WSAPIAdapter(object):

    def __init__(
            self,
            message,
            action_map,
            action_meta_map,
            entity_map,
            namespace_map=None):
        self.message = message
        self.content = json.loads(message.content["text"])

        # Example action map
        # action_map = {
        #         "get": "get",
        #         "list": "list",
        #         "create": "create",
        #         "replace": "update",
        #         "update": "update",
        #         "delete": "delete",
        #     }
        self.action_map = action_map

        # Example action meta map
        # action_meta_map = {
        #     "get": [],
        #     "list": [],
        #     "create": ["uuid"],
        #     "replace": ["uuid"],
        #     "update": ["uuid"],
        #     "delete": ["uuid"],
        # }
        self.action_meta_map = action_meta_map

        # Example entity map
        # namespace_map = {
        #     "model_name": "model-name",
        # }
        self.entity_map = entity_map

        # Example namespace map
        # namespace_map = {
        #     "modelname": "appname-api",
        # }
        self.namespace_map = namespace_map

    def get_kwarg_names_for_url(self, view_name, namespace=None):
        """Get a route url and kwargs given a namespace and a view name."""

        # Get a resolver from the default urls conf. Eg: 'project.urls'
        resolver = get_resolver()

        # If we have a namespace, use namespace dict to find its resolver
        if namespace:
            sub_resolver = resolver.namespace_dict[namespace][1]
            resolver_data = sub_resolver.reverse_dict.get(view_name)
        else:
            resolver_data = resolver.reverse_dict[view_name]

        pattern_list = resolver_data[0]

        '''
        Need to specify the 1st pattern because url regexes can
        potentially have multiple kwarg arrangments - this function does
        not take this possibility into account.
        '''
        first_pattern = pattern_list[0]

        '''
        `first_pattern` is now of the form `(url_string, kwarg_list)` -
        all we are interested in is the 2nd value.
        '''
        return first_pattern[1]

    def get_url_args(self, message):
        action = message["action"]
        entity = message["entity"]

        # Build the view name from the entity and the action.
        # This is a convention.
        # The action map allows us to map specific action to url names.
        view_name = "{entity}-{action}".format(
            entity=self.entity_map[entity],
            action=self.action_map[action],
            )

        if self.namespace_map:
            namespace = self.namespace_map[entity]
            url_name = "{}:{}".format(namespace, view_name)
        else:
            url_name = view_name

        # Extract the required kwargs for a given route
        url_kwargs = self.get_kwarg_names_for_url(view_name, namespace)

        # Build the url parameters dictionary using the required kwargs
        url_parameters = {}
        for arg in url_kwargs:
            if message["meta"].get(arg):
                url_parameters[arg] = message["meta"][arg]
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
        data = None
        if response.data:
            data = json.loads(
                JSONRenderer().render(response.data).decode("utf-8")
            )
        return self.process_response(response.status_code, data)

    def get_response_action(self, status_code):

        if status_code == 400:
            return "validation"

        action = self.content.get("action")

        if action in ["get", "list", "create", "replace", "copy"]:
            return "store"
        elif action == "delete":
            return "remove"
        else:
            return None

    def process_response(self, status_code, data):
        action = self.content.get("action")

        if action is None:
            return None

        entity = self.content.get("entity")

        meta = {}
        for key in self.action_meta_map[action]:
            if data:
                meta[key] = data.get(key)
            elif self.content.get("meta"):
                meta[key] = self.content.get("meta").get(key)

        payload = {
            "action": self.get_response_action(status_code),
            "entity": entity,
            "meta": meta,
            "data": data
        }

        return payload
