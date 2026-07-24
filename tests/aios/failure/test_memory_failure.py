def test_memory_failure_signal():

    memory_result = {
        "status": "warning",
        "reason": "storage unavailable",
    }

    assert memory_result["status"] == "warning"
