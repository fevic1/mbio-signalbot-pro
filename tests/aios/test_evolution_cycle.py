from aios.evolution.pattern_detector import PatternDetector
from aios.evolution.feedback_engine import FeedbackEngine
from aios.evolution.improvement_proposer import ImprovementProposer
from aios.evolution.change_planner import ChangePlanner

from aios.control.change_manager import ChangeManager
from aios.control.approval_workflow import ApprovalWorkflow
from aios.control.audit import ControlAudit
from aios.control.audit_replay import AuditReplay

from aios.audit.logger import AuditLogger



def test_autonomous_evolution_cycle():

    pattern = FeedbackEngine(
        PatternDetector()
    ).analyze(
        [
            {
                "severity": "warning",
                "component": "runtime",
                "message": "latency issue",
            }
        ]
    )[0]


    proposal = ImprovementProposer().propose(
        pattern
    )


    review = {
        "approved": True,
        "governance": {
            "passed": True,
            "policy_version_used": 2,
        },
    }


    request = ChangePlanner().create_change_request(
        proposal,
        review,
    )


    manager = ChangeManager()

    change = ChangePlanner().submit(
        request,
        manager,
    )


    audit = AuditLogger()

    control = ControlAudit(
        audit
    )


    approved = ApprovalWorkflow(
        control
    ).approve(
        change,
        review["governance"],
        {
            "decision_id": "decision-1",
            "council_session": "session-1",
            "policy_version_used": 2,
        },
    )


    assert approved["approved"] is True


    replay = AuditReplay().replay(
        audit.storage.read(
            "changes"
        )
    )


    assert replay[-1]["decision_id"] == "decision-1"
    assert replay[-1]["proposal_id"] == proposal["proposal_id"]
