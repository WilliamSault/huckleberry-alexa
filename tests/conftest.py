"""Shared test fixtures and helpers."""

from unittest.mock import MagicMock, patch
import pytest

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import (
    RequestEnvelope,
    Session,
    Intent,
    Slot,
    SlotConfirmationStatus,
    IntentRequest,
    LaunchRequest,
)
from ask_sdk_model.ui import SimpleCard


def make_intent_input(intent_name: str, slots: dict[str, str] | None = None) -> HandlerInput:
    """Build a minimal HandlerInput for the given intent name and slots."""
    slot_objects = {}
    if slots:
        for name, value in slots.items():
            slot_objects[name] = Slot(
                name=name,
                value=value,
                confirmation_status=SlotConfirmationStatus.NONE,
            )

    intent = Intent(name=intent_name, slots=slot_objects)
    request = IntentRequest(request_id="test-req-id", intent=intent)
    envelope = RequestEnvelope(
        version="1.0",
        session=Session(session_id="test-session-id", new=False),
        request=request,
    )

    handler_input = HandlerInput(request_envelope=envelope)
    # Attach a real ResponseBuilder
    from ask_sdk_core.response_helper import ResponseFactory
    handler_input.response_builder = ResponseFactory()
    return handler_input


def make_launch_input() -> HandlerInput:
    """Build a HandlerInput for a LaunchRequest."""
    request = LaunchRequest(request_id="test-req-id")
    envelope = RequestEnvelope(
        version="1.0",
        session=Session(session_id="test-session-id", new=True),
        request=request,
    )
    handler_input = HandlerInput(request_envelope=envelope)
    from ask_sdk_core.response_helper import ResponseFactory
    handler_input.response_builder = ResponseFactory()
    return handler_input


@pytest.fixture
def mock_run_huckleberry_with_child():
    """Patch run_huckleberry_with_child across all handler modules."""
    targets = [
        "huckleberry_alexa.handlers.nursing.run_huckleberry_with_child",
        "huckleberry_alexa.handlers.diaper.run_huckleberry_with_child",
        "huckleberry_alexa.handlers.bottle.run_huckleberry_with_child",
        "huckleberry_alexa.handlers.status.run_huckleberry_with_child",
    ]
    patchers = [patch(t) for t in targets]
    mocks = [p.start() for p in patchers]
    yield mocks  # yields list; most tests use index 0 for the relevant module
    for p in patchers:
        p.stop()
