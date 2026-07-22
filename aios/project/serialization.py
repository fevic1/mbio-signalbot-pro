from dataclasses import asdict, is_dataclass

def serialize(obj):
    if is_dataclass(obj):
        return asdict(obj)
    return obj
