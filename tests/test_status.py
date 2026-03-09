"""Tests for status handlers and time_since_speech helper."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import pytest

from huckleberry_alexa.handlers.status import (
    LastFeedStatusIntentHandler,
    LastNappyStatusIntentHandler,
    _time_since_speech,
    _get_last_feed_timestamp,
    _get_last_diaper_timestamp,
)
from tests.conftest import make_intent_input


class TestTimeSinceSpeech:
    def test_seconds(self):
        past = datetime.now(timezone.utc) - timedelta(seconds=45)
        result = _time_since_speech(past)
        assert "second" in result

    def test_one_minute(self):
        past = datetime.now(timezone.utc) - timedelta(minutes=1)
        result = _time_since_speech(past)
        assert "1 minute" in result

    def test_plural_minutes(self):
        past = datetime.now(timezone.utc) - timedelta(minutes=30)
        result = _time_since_speech(past)
        assert "30 minutes" in result

    def test_one_hour(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        result = _time_since_speech(past)
        assert "1 hour" in result
        assert "minute" not in result

    def test_hours_and_minutes(self):
        past = datetime.now(timezone.utc) - timedelta(hours=2, minutes=15)
        result = _time_since_speech(past)
        assert "2 hours" in result
        assert "15 minutes" in result

    def test_singular_hour_plural_minutes(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1, minutes=1)
        result = _time_since_speech(past)
        assert "1 hour" in result
        assert "1 minute" in result


def _make_ts(hours_ago: float) -> int:
    """Return a Unix timestamp for hours_ago hours in the past."""
    return int((datetime.now(timezone.utc) - timedelta(hours=hours_ago)).timestamp())


class TestLastFeedStatusIntentHandler:
    handler = LastFeedStatusIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("LastFeedStatusIntent")
        assert self.handler.can_handle(hi)

    def test_cannot_handle_other_intent(self):
        hi = make_intent_input("SomeOtherIntent")
        assert not self.handler.can_handle(hi)

    def test_returns_elapsed_time(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (_make_ts(2.25), "Frederica")
            hi = make_intent_input("LastFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "feed" in ssml
            assert "hour" in ssml

    def test_no_feed_found(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (None, "Frederica")
            hi = make_intent_input("LastFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "couldn't find" in ssml

    def test_child_not_found(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.side_effect = ValueError("I couldn't find a child named Bob. Available children are Frederica.")
            hi = make_intent_input("LastFeedStatusIntent", {"child": "Bob"})
            response = self.handler.handle(hi)
            assert "couldn't find" in response.output_speech.ssml.lower()


class TestLastNappyStatusIntentHandler:
    handler = LastNappyStatusIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("LastNappyStatusIntent")
        assert self.handler.can_handle(hi)

    def test_returns_elapsed_time(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (_make_ts(1.5), "Frederica")
            hi = make_intent_input("LastNappyStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "nappy" in ssml
            assert "hour" in ssml or "minute" in ssml

    def test_no_nappy_found(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (None, "Frederica")
            hi = make_intent_input("LastNappyStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "couldn't find" in ssml
