from aios.supervisor.recovery import RecoveryPlanner


def test_failed_runtime_creates_recovery():

    proposal = RecoveryPlanner().create(
        {
            "status": "failed"
        }
    )

    assert proposal.action == "prepare_recovery"
