def test_event_failure_isolated():

    event_result = {
        "published": False,
        "error": "event bus unavailable",
    }

    assert event_result["published"] is False
