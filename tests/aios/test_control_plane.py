from aios.control.change_manager import ChangeManager
from aios.control.approval_workflow import ApprovalWorkflow
from aios.control.rollback_manager import RollbackManager
from aios.control.audit_replay import AuditReplay
from aios.audit.logger import AuditLogger
from aios.control.audit import ControlAudit



def test_control_plane_flow():

    audit = AuditLogger()

    control_audit = ControlAudit(
        audit
    )


    change_manager = ChangeManager()


    change = change_manager.create(
        "execution",
        "upgrade",
        True,
    )


    result = ApprovalWorkflow(
        control_audit
    ).approve(
        change,
        {
            "passed": True
        },
        {
            "policy_version_used": 2,
            "decision_id": "decision-1",
            "council_session": "session-1",
        }
    )


    assert result["approved"] is True


    records = audit.storage.read(
        "changes"
    )


    replay = AuditReplay().replay(
        records
    )


    assert replay[-1]["decision_id"] == "decision-1"


    rollback = RollbackManager()

    rollback.register(
        change["change_id"],
        {
            "version": "previous"
        }
    )


    assert rollback.rollback(
        change["change_id"]
    )["rolled_back"] is True
