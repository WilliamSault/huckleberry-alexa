"""Tests for bottle feed handler."""

from unittest.mock import patch, AsyncMock, MagicMock
import pytest

from huckleberry_alexa.handlers.bottle import LogBottleFeedIntentHandler
from tests.conftest import make_intent_input


class TestLogBottleFeedIntentHandler:
    handler = LogBottleFeedIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("LogBottleFeedIntent")
        assert self.handler.can_handle(hi)

    def test_cannot_handle_other_intent(self):
        hi = make_intent_input("SomeOtherIntent")
        assert not self.handler.can_handle(hi)

    def test_log_bottle_with_amount(self):
        with patch("huckleberry_alexa.handlers.bottle.run_huckleberry_with_child") as m:
            m.return_value = (None, "Frederica")
            hi = make_intent_input("LogBottleFeedIntent", {"amount": "80"})
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "80" in ssml
            assert "bottle" in ssml
            assert "Frederica" in response.output_speech.ssml

    def test_log_bottle_uses_last_amount_when_none_given(self):
        with patch("huckleberry_alexa.handlers.bottle.run_huckleberry_with_child") as m:
            # First call: returns last bottle amount (120)
            # Second call: logs the feed
            m.side_effect = [(120, "Frederica"), (None, "Frederica")]
            hi = make_intent_input("LogBottleFeedIntent", {})
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "120" in ssml
            assert "bottle" in ssml

    def test_log_bottle_asks_for_amount_when_no_history(self):
        with patch("huckleberry_alexa.handlers.bottle.run_huckleberry_with_child") as m:
            m.return_value = (None, "Frederica")
            hi = make_intent_input("LogBottleFeedIntent", {})
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "couldn't find" in ssml or "please say" in ssml

    def test_child_not_found(self):
        with patch("huckleberry_alexa.handlers.bottle.run_huckleberry_with_child") as m:
            m.side_effect = ValueError("I couldn't find a child named Bob. Available children are Frederica.")
            hi = make_intent_input("LogBottleFeedIntent", {"amount": "100", "child": "Bob"})
            response = self.handler.handle(hi)
            assert "couldn't find" in response.output_speech.ssml.lower()
