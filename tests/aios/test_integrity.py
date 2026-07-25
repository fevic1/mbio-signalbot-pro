from aios.integrity.health import IntegrityHealth
from aios.integrity.architecture import ArchitectureGuard
from aios.integrity.dependency import DependencyGuard
from aios.integrity.memory import MemoryGuard


def test_integrity_health():

    health = IntegrityHealth(
        [
            ArchitectureGuard(),
            DependencyGuard(),
            MemoryGuard(),
        ]
    )


    result = health.check()


    assert result["healthy"] is True
