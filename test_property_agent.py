from property_agent import needs_human_review


def test_urgent_request_is_sent_to_human_review():
    request = {"request_id": "maint-1", "property_id": "unit-7b", "priority": "urgent"}
    assert needs_human_review(request, {"unit-7b"}, False) is True


def test_complete_normal_request_stays_in_agent_queue():
    request = {"request_id": "maint-2", "property_id": "unit-7b", "priority": "normal"}
    assert needs_human_review(request, {"unit-7b"}, False) is False
