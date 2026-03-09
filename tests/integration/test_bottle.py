"""Integration tests for bottle feed logging."""

from datetime import datetime, timedelta, timezone

import pytest

from huckleberry_alexa.handlers.bottle import _get_last_bottle_amount
from huckleberry_alexa.huckleberry_client import run_huckleberry_with_child

pytestmark = pytest.mark.integration


async def test_log_bottle_records_interval(api, test_child_uid):
    await api.log_bottle(test_child_uid, amount=75)

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)
    intervals = await api.list_feed_intervals(
        test_child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )

    matching = [
        i for i in intervals
        if getattr(i, "mode", None) == "bottle" and getattr(i, "amount", None) == 75
    ]
    assert matching, "Expected a bottle interval with amount=75 in the last 5 minutes"


def test_last_bottle_amount_lookup():
    # Log 90ml then verify _get_last_bottle_amount returns 90
    run_huckleberry_with_child(
        lambda api, uid: api.log_bottle(uid, amount=90),
        child_name="Test",
    )
    amount, _ = run_huckleberry_with_child(
        _get_last_bottle_amount,
        child_name="Test",
    )
    assert amount == 90
