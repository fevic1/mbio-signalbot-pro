from aios.operations.deployment_guard import DeploymentGuard
from aios.operations.runtime_policy import RuntimePolicy
from aios.operations.config_validation import ConfigValidator
from aios.operations.incident_manager import IncidentManager



def test_deployment_guard_pass():

    result = DeploymentGuard().check(
        {
            "approved": True,
            "rollback_available": True,
        }
    )

    assert result["passed"] is True



def test_deployment_guard_fail():

    result = DeploymentGuard().check(
        {
            "approved": False,
            "rollback_available": False,
        }
    )

    assert result["passed"] is False

    assert len(
        result["failures"]
    ) == 2



def test_runtime_policy_pass():

    result = RuntimePolicy().validate(
        {
            "governance_enabled": True,
        }
    )

    assert result["allowed"] is True



def test_runtime_policy_fail():

    result = RuntimePolicy().validate(
        {
            "governance_enabled": False,
        }
    )

    assert result["allowed"] is False



def test_config_validator():

    validator = ConfigValidator(
        [
            "API_KEY",
            "DATABASE",
        ]
    )

    result = validator.validate(
        {
            "API_KEY": "test"
        }
    )

    assert result["valid"] is False

    assert "DATABASE" in result["missing"]



def test_incident_manager():

    manager = IncidentManager()

    incident = manager.record(
        "failure",
        "runtime",
    )

    assert incident["component"] == "runtime"

    assert len(
        manager.history()
    ) == 1
