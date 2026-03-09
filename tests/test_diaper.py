"""Tests for diaper/nappy handler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
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

    def _call_coro_factory(self, mock_client):
        """Extract and invoke the coro_factory captured by mock_client."""
        coro_factory = mock_client.call_args[0][0]
        mock_api = MagicMock()
        mock_api.log_diaper = AsyncMock()
        asyncio.run(coro_factory(mock_api, "child-uid"))
        return mock_api

    def test_log_nappy_no_type_defaults_to_both(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {})
        self.handler.handle(hi)
        mock_api = self._call_coro_factory(mock_client)
        mock_api.log_diaper.assert_called_once_with("child-uid", mode="both", color=None)

    def test_log_nappy_pee_type(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {"nappy_type": "pee"})
        response = self.handler.handle(hi)
        mock_api = self._call_coro_factory(mock_client)
        mock_api.log_diaper.assert_called_once_with("child-uid", mode="pee", color=None)
        assert "pee" in response.output_speech.ssml.lower()

    def test_log_nappy_pee_color_ignored(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {"nappy_type": "pee", "color": "yellow"})
        response = self.handler.handle(hi)
        mock_api = self._call_coro_factory(mock_client)
        mock_api.log_diaper.assert_called_once_with("child-uid", mode="pee", color=None)
        assert "yellow" not in response.output_speech.ssml.lower()

    def test_log_nappy_wet_synonym(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {"nappy_type": "wet"})
        self.handler.handle(hi)
        mock_api = self._call_coro_factory(mock_client)
        mock_api.log_diaper.assert_called_once_with("child-uid", mode="pee", color=None)

    def test_log_nappy_poo_type(self, mock_client):
        hi = make_intent_input("LogNappyIntent", {"nappy_type": "poo"})
        self.handler.handle(hi)
        mock_api = self._call_coro_factory(mock_client)
        mock_api.log_diaper.assert_called_once_with("child-uid", mode="poo", color=None)

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
