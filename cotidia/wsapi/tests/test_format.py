from django.test import TestCase

from cotidia.wsapi.utils.format import format_message


class FormatTests(TestCase):
    def test_format_message(self):
        """Test a message output from variables."""

        action = "create"
        entity = "model"
        data = {"name": "test"}
        meta = {"uuid": 1234}

        output = format_message(action, entity)
        self.assertEqual(
            output,
            {
                "action": "create",
                "entity": "model",
                "data": {}
            })

        output = format_message(action, entity, data)
        self.assertEqual(
            output,
            {
                "action": "create",
                "entity": "model",
                "data": {
                    "name": "test"
                    }
            })

        output = format_message(action, entity, data, meta)
        self.assertEqual(
            output,
            {
                "action": "create",
                "entity": "model",
                "data": {
                    "name": "test"
                    },
                "meta": {
                    "uuid": 1234
                    }
            })
