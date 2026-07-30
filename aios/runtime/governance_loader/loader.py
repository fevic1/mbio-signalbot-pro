from pathlib import Path

from .models import GovernanceContext


class GovernanceLoader:

    def __init__(self, root_dir=None):
        self.root = Path(root_dir or ".")
        self.path = (
            self.root
            / ".aios"
            / "governance"
        )

    def load(self):

        return GovernanceContext(
            version="AIOS v2.1",
            constitution=self._read(
                "llm_operating_constitution.md"
            ),
            security_rules=self._read(
                "security_operating_rules.md"
            ),
            reliability_rules=self._read(
                "reliability_rules.md"
            ),
            constraints=[
                "max_retries=3",
                "safe_mode_enabled=true",
                "telemetry_required=true",
                "human_approval_required_for_red_lines=true",
            ],
            metadata={
                "governance_loaded": True,
            },
        )

    def _read(self, filename):

        path = self.path / filename

        if not path.exists():
            raise FileNotFoundError(path)

        return path.read_text(
            encoding="utf-8"
        )
