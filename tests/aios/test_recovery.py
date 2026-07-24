from aios.supervisor.recovery import (
    RecoveryPlanner,
)


def test_warning_creates_recovery():

    proposal = RecoveryPlanner().create(
        {
            "status": "warning"
        }
    )

    assert proposal.action == "inspect_runtime"
