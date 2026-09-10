from server.workflow.states import Validation


def test_validation_accepts_reason_only_payload():
    payload = {"reason": "NONE"}

    validation = Validation.model_validate(payload)

    assert validation.flag is True
    assert validation.reason == "NONE"
