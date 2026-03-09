"""Integration tests for nursing lifecycle via the Huckleberry API."""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


async def test_start_nursing_left(api, test_child_uid):
    await api.start_nursing(test_child_uid, side="left")


async def test_start_nursing_right(api, test_child_uid):
    await api.start_nursing(test_child_uid, side="right")


async def test_start_and_complete_records_interval(api, test_child_uid):
    await api.start_nursing(test_child_uid, side="left")
    await asyncio.sleep(1)
    await api.complete_nursing(test_child_uid)

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)
    intervals = await api.list_feed_intervals(
        test_child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )

    matching = [
        i for i in intervals
        if getattr(i, "mode", None) == "breast" and getattr(i, "lastSide", None) == "left"
    ]
    assert matching, "Expected a completed breast-left interval in the last 5 minutes"


async def test_pause_and_complete(api, test_child_uid):
    await api.start_nursing(test_child_uid, side="left")
    await api.pause_nursing(test_child_uid)
    await api.complete_nursing(test_child_uid)


async def test_switch_then_complete(api, test_child_uid):
    await api.start_nursing(test_child_uid, side="left")
    await asyncio.sleep(1)
    await api.switch_nursing(test_child_uid)
    await asyncio.sleep(1)
    await api.complete_nursing(test_child_uid)

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)
    intervals = await api.list_feed_intervals(
        test_child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )

    matching = [
        i for i in intervals
        if getattr(i, "mode", None) == "breast" and getattr(i, "rightDuration", 0) > 0
    ]
    assert matching, "Expected a breast interval with rightDuration > 0 after switch"
