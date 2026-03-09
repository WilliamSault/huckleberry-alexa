"""Integration tests for status timestamp lookups."""

import time

import pytest

from huckleberry_alexa.handlers.status import (
    _get_last_diaper_timestamp,
    _get_last_feed_timestamp,
)
from huckleberry_alexa.huckleberry_client import run_huckleberry_with_child

pytestmark = pytest.mark.integration


def test_last_feed_timestamp_after_bottle():
    run_huckleberry_with_child(
        lambda api, uid: api.log_bottle(uid, amount=80),
        child_name="Test",
    )
    before = int(time.time())
    ts, _ = run_huckleberry_with_child(_get_last_feed_timestamp, child_name="Test")
    assert ts is not None
    assert ts >= before - 60, f"Expected timestamp within last 60s, got {ts} vs now {before}"


def test_last_nappy_timestamp_after_diaper():
    run_huckleberry_with_child(
        lambda api, uid: api.log_diaper(uid, mode="wet"),
        child_name="Test",
    )
    before = int(time.time())
    ts, _ = run_huckleberry_with_child(_get_last_diaper_timestamp, child_name="Test")
    assert ts is not None
    assert ts >= before - 60, f"Expected timestamp within last 60s, got {ts} vs now {before}"


def test_last_feed_status_speech():
    """Smoke test: run _get_last_feed_timestamp and format like the handler would."""
    from datetime import datetime, timezone

    from huckleberry_alexa.handlers.status import _time_since_speech

    ts, resolved = run_huckleberry_with_child(_get_last_feed_timestamp, child_name="Test")

    if ts is None:
        speech = f"I couldn't find any feeds for {resolved} in the last 48 hours."
    else:
        elapsed = _time_since_speech(datetime.fromtimestamp(ts, tz=timezone.utc))
        speech = f"The last feed for {resolved} was {elapsed} ago."

    assert "ago" in speech or "couldn't find" in speech
