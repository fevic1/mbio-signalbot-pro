def check_kernel(kernel):
    return {
        "state": str(kernel.state),
        "services": len(kernel.services),
    }


def check_supervisor(kernel):
    return {
        "supervised": len(kernel.supervisor),
        "healthy": len(kernel.supervisor.healthy()),
        "failed": len(kernel.supervisor.failed()),
    }


def check_lifecycle(kernel):
    return {
        "events": len(kernel.lifecycle.history()),
        "latest": (
            kernel.lifecycle.latest().phase.value
            if kernel.lifecycle.latest()
            else None
        ),
    }


def check_events(kernel):
    return {
        "event_bus": type(kernel.event_bus).__name__,
    }


def check_governance(kernel):

    request = kernel.approval_manager.create_request(
        action="verify_execution",
        requested_by="runtime_verifier",
    )

    kernel.approval_manager.approve(
        request["id"],
        approved_by="verification",
    )

    approved = kernel.approval_manager.get(
        request["id"]
    )

    return {
        "status": approved["status"],
        "approved_by": approved["approved_by"],
    }


def check_execution(kernel):

    result = kernel.execution_orchestrator.run_mission(
        [
            {
                "milestone": "research",
                "tasks": [
                    {
                        "name": "verification_task"
                    }
                ],
            }
        ],
        type(
            "Team",
            (),
            {
                "agents": [
                    type(
                        "Agent",
                        (),
                        {
                            "name": "verifier",
                            "role": "Researcher",
                        }
                    )()
                ]
            }
        )(),
    )

    return {
        "has_result": bool(result),
        "governance_checked": "governance" in result,
    }


def check_audit(kernel):

    return {
        "audit_available": hasattr(
            kernel,
            "audit_logger"
        ),
    }


def check_execution_audit(kernel):

    return {
        "handler": type(
            kernel.execution_audit_handler
        ).__name__,

        "records": len(
            kernel.audit.all()
        ),
    }
