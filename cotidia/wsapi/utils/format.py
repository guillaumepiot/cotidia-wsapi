def format_message(action, entity, data=None, meta=None):
    payload = {
        "action": action,
        "entity": entity
    }

    if data:
        payload["data"] = data

    if meta:
        payload["meta"] = meta

    return payload
