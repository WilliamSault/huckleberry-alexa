"""Tests for nursing handlers."""

from unittest.mock import patch, MagicMock
import pytest

from huckleberry_alexa.handlers.nursing import (
    StartNursingIntentHandler,
    PauseNursingIntentHandler,
    SwitchBreastIntentHandler,
    StopNursingIntentHandler,
)
from tests.conftest import make_intent_input


@pytest.fixture
def mock_client():
    with patch("huckleberry_alexa.handlers.nursing.run_huckleberry_with_child") as m:
        m.return_value = (None, "Frederica")
        yield m


class TestStartNursingIntentHandler:
    handler = StartNursingIntentHandler()

    def test_can_handle_start_nursing(self):
        hi = make_intent_input("StartNursingIntent", {"side": "left"})
        assert self.handler.can_handle(hi)

    def test_cannot_handle_other_intent(self):
        hi = make_intent_input("SomeOtherIntent")
        assert not self.handler.can_handle(hi)

    def test_start_left_breast(self, mock_client):
        hi = make_intent_input("StartNursingIntent", {"side": "left"})
        response = self.handler.handle(hi)
        assert "left" in response.output_speech.ssml.lower()
        assert "Frederica" in response.output_speech.ssml
        mock_client.assert_called_once()

    def test_start_right_breast(self, mock_client):
        hi = make_intent_input("StartNursingIntent", {"side": "right"})
        response = self.handler.handle(hi)
        assert "right" in response.output_speech.ssml.lower()

    def test_missing_side_asks_for_clarification(self):
        hi = make_intent_input("StartNursingIntent", {})
        response = self.handler.handle(hi)
        ssml = response.output_speech.ssml.lower()
        assert "which side" in ssml or "left or right" in ssml

    def test_child_not_found_returns_error(self):
        with patch("huckleberry_alexa.handlers.nursing.run_huckleberry_with_child") as m:
            m.side_effect = ValueError("I couldn't find a child named Bob. Available children are Frederica.")
            hi = make_intent_input("StartNursingIntent", {"side": "left", "child": "Bob"})
            response = self.handler.handle(hi)
            assert "couldn't find" in response.output_speech.ssml.lower()


class TestPauseNursingIntentHandler:
    handler = PauseNursingIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("PauseNursingIntent")
        assert self.handler.can_handle(hi)

    def test_pause_feed(self, mock_client):
        hi = make_intent_input("PauseNursingIntent")
        response = self.handler.handle(hi)
        assert "pause" in response.output_speech.ssml.lower()
        mock_client.assert_called_once()


class TestSwitchBreastIntentHandler:
    handler = SwitchBreastIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("SwitchBreastIntent")
        assert self.handler.can_handle(hi)

    def test_switch_breast(self, mock_client):
        hi = make_intent_input("SwitchBreastIntent")
        response = self.handler.handle(hi)
        assert "switch" in response.output_speech.ssml.lower()
        mock_client.assert_called_once()


class TestStopNursingIntentHandler:
    handler = StopNursingIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("StopNursingIntent")
        assert self.handler.can_handle(hi)

    def test_stop_feed(self, mock_client):
        hi = make_intent_input("StopNursingIntent")
        response = self.handler.handle(hi)
        ssml = response.output_speech.ssml.lower()
        assert "saved" in ssml or "feed" in ssml
        mock_client.assert_called_once()
