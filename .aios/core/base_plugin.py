#!/usr/bin/env python3

import importlib.util
from pathlib import Path

_core = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location(
    "context",
    _core / "context.py"
)

context_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_module)

Context = context_module.Context


class BasePlugin:
    NAME = "plugin"
    VERSION = "0.0.1"

    def initialize(self, services):
        self.services = services
        self.context = Context(
            services,
            plugin=self.NAME,
        )

    def on_load(self):
        pass

    def on_unload(self):
        pass

    def health(self):
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "status": "healthy",
        }
