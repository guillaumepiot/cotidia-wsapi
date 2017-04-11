def format_message(action, entity=None, data=None, meta=None):
    payload = {
        "action": action
    }

    if data:
        payload["entity"] = entity

    if data:
        payload["data"] = data

    if meta:
        payload["meta"] = meta

    return payload
