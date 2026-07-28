#!/usr/bin/env python3

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.base_plugin import BasePlugin

class SuperpowersPlugin(BasePlugin):
    NAME = "superpowers"
    VERSION = "1.0.0"

    def on_load(self):
        self.context.logger.info(
            "Plugin loaded",
            plugin=self.NAME
        )

    def on_unload(self):
        self.context.logger.info(
            "Plugin unloaded",
            plugin=self.NAME
        )
