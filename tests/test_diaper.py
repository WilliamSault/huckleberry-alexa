"""Tests for diaper/nappy handler."""

from unittest.mock import patch
import pytest

from huckleberry_alexa.handlers.diaper import LogNappyIntentHandler
from tests.conftest import make_intent_input


@pytest.fixture
def mock_client():
    with patch("huckleberry_alexa.handlers.diaper.run_huckleberry_with_child") as m:
        m.return_value = (None, "Frederica")
        yield m


class TestLogNappyIntentHandler:
    handler = LogNappyIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("LogNappyIntent")
        assert self.handler.can_handle(hi)

    def test_cannot_handle_other_intent(self):
        hi = make_intent_input("SomeOtherIntent")
        assert not self.handler.can_handle(hi)

    def test_log_nappy_no_color(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {})
        response = self.handler.handle(hi)
        ssml = response.output_speech.ssml.lower()
        assert "nappy" in ssml
        assert "Frederica" in response.output_speech.ssml
        mock_client.assert_called_once()

    def test_log_nappy_with_color(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {"color": "yellow"})
        response = self.handler.handle(hi)
        ssml = response.output_speech.ssml.lower()
        assert "yellow" in ssml
        assert "nappy" in ssml

    def test_log_nappy_green(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {"color": "green"})
        response = self.handler.handle(hi)
        assert "green" in response.output_speech.ssml.lower()

    def test_child_not_found(self):
        with patch("huckleberry_alexa.handlers.diaper.run_huckleberry_with_child") as m:
            m.side_effect = ValueError("I couldn't find a child named Bob. Available children are Frederica.")
            hi = make_intent_input("LogNappyIntent", {"child": "Bob"})
            response = self.handler.handle(hi)
            assert "couldn't find" in response.output_speech.ssml.lower()
