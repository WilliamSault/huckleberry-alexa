"""Integration tests for diaper logging."""

from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


async def test_log_diaper_with_color(api, test_child_uid):
    await api.log_diaper(test_child_uid, mode="both", color="yellow")

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)
    intervals = await api.list_diaper_intervals(
        test_child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )

    matching = [
        i for i in intervals
        if getattr(i, "mode", None) == "both" and getattr(i, "color", None) == "yellow"
    ]
    assert matching, "Expected a diaper interval with mode='both' and color='yellow'"


async def test_log_diaper_no_color(api, test_child_uid):
    await api.log_diaper(test_child_uid, mode="both")

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)
    intervals = await api.list_diaper_intervals(
        test_child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )

    matching = [
        i for i in intervals
        if getattr(i, "mode", None) == "both" and getattr(i, "color", None) is None
    ]
    assert matching, "Expected a diaper interval with mode='both' and no color"
