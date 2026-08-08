"""
MBIO Recovery Manager
"""

import logging

logger = logging.getLogger(__name__)


class RecoveryModule:
    name = "base"

    async def discover(self):
        pass

    async def recover(self):
        pass

    async def validate(self):
        pass

    async def repair(self):
        pass


class RecoveryManager:

    def __init__(self):
        self.modules = []

    def register(self, module):
        self.modules.append(module)

    async def run(self):

        logger.info("=" * 70)
        logger.info("MBIO RECOVERY START")
        logger.info("=" * 70)

        for module in self.modules:

            logger.info("▶ %s", module.name)

            await module.discover()
            await module.recover()
            await module.validate()
            await module.repair()

            logger.info("✓ %s", module.name)

        logger.info("=" * 70)
        logger.info("MBIO RECOVERY COMPLETE")
        logger.info("=" * 70)


recovery_manager = RecoveryManager()
