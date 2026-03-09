"""Tests for status handlers and time_since_speech helper."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import pytest

from huckleberry_alexa.handlers.status import (
    LastFeedStatusIntentHandler,
    LastNappyStatusIntentHandler,
    CurrentFeedStatusIntentHandler,
    _time_since_speech,
    _seconds_to_speech,
    _get_last_feed_info,
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


class TestSecondToSpeech:
    def test_seconds(self):
        assert "45 seconds" in _seconds_to_speech(45)

    def test_one_second(self):
        assert "1 second" == _seconds_to_speech(1)

    def test_minutes(self):
        assert "5 minutes" in _seconds_to_speech(300)

    def test_one_minute(self):
        assert "1 minute" == _seconds_to_speech(60)

    def test_hours_and_minutes(self):
        result = _seconds_to_speech(3900)  # 1h 5m
        assert "1 hour" in result
        assert "5 minutes" in result

    def test_exact_hours(self):
        assert "2 hours" == _seconds_to_speech(7200)


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

    def test_returns_elapsed_time_breast_with_side(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = ((_make_ts(2.25), "breast", "left"), "Frederica")
            hi = make_intent_input("LastFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "feed" in ssml
            assert "hour" in ssml
            assert "left breast" in ssml

    def test_returns_elapsed_time_breast_side_none(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = ((_make_ts(1.0), "breast", "none"), "Frederica")
            hi = make_intent_input("LastFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "feed" in ssml
            assert "breast" not in ssml

    def test_returns_elapsed_time_bottle(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = ((_make_ts(0.5), "bottle", None), "Frederica")
            hi = make_intent_input("LastFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "feed" in ssml
            assert "breast" not in ssml

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


def _make_timer(active=True, paused=False, feed_start_offset=600, timer_start_offset=120,
                active_side="left", left_duration=180.0, right_duration=0.0):
    """Build a mock feed timer object."""
    import time
    now = time.time()
    timer = MagicMock()
    timer.active = active
    timer.paused = paused
    timer.feedStartTime = now - feed_start_offset
    timer.timerStartTime = now - timer_start_offset
    timer.activeSide = active_side
    timer.leftDuration = left_duration
    timer.rightDuration = right_duration
    return timer


class TestCurrentFeedStatusIntentHandler:
    handler = CurrentFeedStatusIntentHandler()

    def test_can_handle(self):
        hi = make_intent_input("CurrentFeedStatusIntent")
        assert self.handler.can_handle(hi)

    def test_cannot_handle_other_intent(self):
        hi = make_intent_input("SomeOtherIntent")
        assert not self.handler.can_handle(hi)

    def test_no_active_feed(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (None, "Frederica")
            hi = make_intent_input("CurrentFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "no active feed" in ssml

    def test_inactive_timer(self):
        timer = _make_timer(active=False)
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (timer, "Frederica")
            hi = make_intent_input("CurrentFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "no active feed" in ssml

    def test_active_feed_includes_side_and_durations(self):
        # feed started 10 min ago, current left segment started 2 min ago
        # left accumulated = 3 min, right = 0
        timer = _make_timer(
            active=True, paused=False,
            feed_start_offset=600, timer_start_offset=120,
            active_side="left", left_duration=180.0, right_duration=0.0,
        )
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (timer, "Frederica")
            hi = make_intent_input("CurrentFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            assert "frederica" in ssml
            assert "left" in ssml
            assert "left breast" in ssml
            assert "right breast" in ssml

    def test_paused_feed_segment_not_added(self):
        # paused: elapsed_segment should be 0
        timer = _make_timer(
            active=True, paused=True,
            feed_start_offset=600, timer_start_offset=120,
            active_side="right", left_duration=240.0, right_duration=60.0,
        )
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.return_value = (timer, "Frederica")
            hi = make_intent_input("CurrentFeedStatusIntent")
            response = self.handler.handle(hi)
            ssml = response.output_speech.ssml.lower()
            # Should still mention left and right breast durations
            assert "left breast" in ssml
            assert "right breast" in ssml

    def test_child_not_found(self):
        with patch("huckleberry_alexa.handlers.status.run_huckleberry_with_child") as m:
            m.side_effect = ValueError("I couldn't find a child named Bob.")
            hi = make_intent_input("CurrentFeedStatusIntent", {"child": "Bob"})
            response = self.handler.handle(hi)
            assert "couldn't find" in response.output_speech.ssml.lower()
