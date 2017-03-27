def format_message(action, entity, data={}, meta=None):
    payload = {
        "action": action,
        "entity": entity,
        "data": data
    }

    if meta:
        payload["meta"] = meta

    return payload
