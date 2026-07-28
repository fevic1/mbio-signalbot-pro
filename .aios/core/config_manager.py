#!/usr/bin/env python3

import os
from copy import deepcopy


class ConfigManager:
    def __init__(self):
        self._config = {}

    def load(self, data: dict):
        self._config = deepcopy(data)

    def get(self, key, default=None):
        current = self._config
        for part in key.split("."):
            if not isinstance(current, dict):
                return default
            if part not in current:
                return default
            current = current[part]
        return current

    def set(self, key, value):
        current = self._config
        parts = key.split(".")

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        current[parts[-1]] = value

    def apply_env(self, prefix="AIOS_"):
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            path = (
                key[len(prefix):]
                .lower()
                .replace("__", ".")
            )

            self.set(path, value)

    def dump(self):
        return deepcopy(self._config)


config = ConfigManager()


if __name__ == "__main__":
    config.load({
        "system": {
            "mode": "development"
        },
        "llm": {
            "provider": "openai"
        }
    })

    config.set("trading.exchange", "hyperliquid")

    print(config.get("system.mode"))
    print(config.get("llm.provider"))
    print(config.get("trading.exchange"))
