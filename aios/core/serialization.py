from dataclasses import asdict, is_dataclass


def serialize(obj):
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"{type(obj).__name__} is not a dataclass")
