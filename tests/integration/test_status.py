"""Integration tests for status timestamp lookups."""

import time

import pytest

from huckleberry_alexa.handlers.status import (
    _get_last_diaper_timestamp,
    _get_last_feed_info,
)
from huckleberry_alexa.huckleberry_client import run_huckleberry_with_child

pytestmark = pytest.mark.integration


def test_last_feed_info_after_bottle():
    run_huckleberry_with_child(
        lambda api, uid: api.log_bottle(uid, amount=80),
        child_name="Test",
    )
    before = int(time.time())
    result, _ = run_huckleberry_with_child(_get_last_feed_info, child_name="Test")
    assert result is not None
    ts, mode, last_side = result
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
    """Smoke test: run _get_last_feed_info and format like the handler would."""
    from datetime import datetime, timezone

    from huckleberry_alexa.handlers.status import _time_since_speech

    result, resolved = run_huckleberry_with_child(_get_last_feed_info, child_name="Test")

    if result is None:
        speech = f"I couldn't find any feeds for {resolved} in the last 48 hours."
    else:
        ts, mode, last_side = result
        elapsed = _time_since_speech(datetime.fromtimestamp(ts, tz=timezone.utc))
        if mode == "breast" and last_side and last_side != "none":
            speech = f"The last feed for {resolved} was {elapsed} ago, on the {last_side} breast."
        else:
            speech = f"The last feed for {resolved} was {elapsed} ago."

    assert "ago" in speech or "couldn't find" in speech
