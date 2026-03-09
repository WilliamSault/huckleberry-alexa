"""Status handlers: LastFeedStatusIntent, LastNappyStatusIntent, CurrentFeedStatusIntent."""

import time
from datetime import datetime, timezone, timedelta

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name
from ask_sdk_model import Response

from huckleberry_alexa.huckleberry_client import run_huckleberry_with_child


def _get_slot_value(handler_input: HandlerInput, slot_name: str) -> str | None:
    slots = handler_input.request_envelope.request.intent.slots
    if slots and slot_name in slots and slots[slot_name].value:
        return slots[slot_name].value
    return None


def _time_since_speech(past: datetime) -> str:
    """Return a human-readable string describing how long ago a datetime was."""
    now = datetime.now(timezone.utc)
    delta = now - past
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds} second{'s' if total_seconds != 1 else ''}"

    total_minutes = total_seconds // 60
    if total_minutes < 60:
        return f"{total_minutes} minute{'s' if total_minutes != 1 else ''}"

    hours = total_minutes // 60
    minutes = total_minutes % 60

    hours_str = f"{hours} hour{'s' if hours != 1 else ''}"
    if minutes == 0:
        return hours_str
    minutes_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{hours_str} and {minutes_str}"


def _seconds_to_speech(seconds: float) -> str:
    """Convert a duration in seconds to a human-readable string."""
    total_seconds = int(seconds)

    if total_seconds < 60:
        return f"{total_seconds} second{'s' if total_seconds != 1 else ''}"

    total_minutes = total_seconds // 60
    if total_minutes < 60:
        return f"{total_minutes} minute{'s' if total_minutes != 1 else ''}"

    hours = total_minutes // 60
    minutes = total_minutes % 60

    hours_str = f"{hours} hour{'s' if hours != 1 else ''}"
    if minutes == 0:
        return hours_str
    minutes_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{hours_str} and {minutes_str}"


async def _get_last_feed_info(api, child_uid: str) -> tuple[int, str, str | None] | None:
    """Return (timestamp, mode, last_side) for the most recent feed, or None."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=48)
    intervals = await api.list_feed_intervals(
        child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )
    if not intervals:
        return None
    interval = max(intervals, key=lambda x: x.start)
    mode = getattr(interval, "mode", None) or "unknown"
    last_side = getattr(interval, "lastSide", None) if mode == "breast" else None
    return int(interval.start), mode, last_side


async def _get_last_diaper_timestamp(api, child_uid: str) -> int | None:
    """Return the Unix timestamp (seconds) of the most recent diaper, or None."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=48)
    intervals = await api.list_diaper_intervals(
        child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )
    if not intervals:
        return None
    return int(max(intervals, key=lambda x: x.start).start)


async def _get_current_feed_timer(api, child_uid: str):
    """Return FirebaseFeedTimerData for the active feed, or None."""
    from huckleberry_api.firebase_types import FirebaseFeedDocumentData

    client = await api._get_firestore_client()
    doc = await client.collection("feed").document(child_uid).get(timeout=10.0)
    if not doc.exists:
        return None
    return FirebaseFeedDocumentData.model_validate(doc.to_dict() or {}).timer


class LastFeedStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("LastFeedStatusIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        child_name = _get_slot_value(handler_input, "child")

        try:
            result, resolved = run_huckleberry_with_child(
                _get_last_feed_info,
                child_name=child_name,
            )
        except ValueError as e:
            return handler_input.response_builder.speak(str(e)).response

        if result is None:
            speak = f"I couldn't find any feeds for {resolved} in the last 48 hours."
        else:
            last_ts, mode, last_side = result
            elapsed = _time_since_speech(datetime.fromtimestamp(last_ts, tz=timezone.utc))
            if mode == "breast" and last_side and last_side != "none":
                speak = f"The last feed for {resolved} was {elapsed} ago, on the {last_side} breast."
            else:
                speak = f"The last feed for {resolved} was {elapsed} ago."

        return handler_input.response_builder.speak(speak).response


class LastNappyStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("LastNappyStatusIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        child_name = _get_slot_value(handler_input, "child")

        try:
            last_ts, resolved = run_huckleberry_with_child(
                _get_last_diaper_timestamp,
                child_name=child_name,
            )
        except ValueError as e:
            return handler_input.response_builder.speak(str(e)).response

        if last_ts is None:
            speak = f"I couldn't find any nappy changes for {resolved} in the last 48 hours."
        else:
            elapsed = _time_since_speech(datetime.fromtimestamp(last_ts, tz=timezone.utc))
            speak = f"The last nappy change for {resolved} was {elapsed} ago."

        return handler_input.response_builder.speak(speak).response


class CurrentFeedStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("CurrentFeedStatusIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        child_name = _get_slot_value(handler_input, "child")

        try:
            timer, resolved = run_huckleberry_with_child(
                _get_current_feed_timer,
                child_name=child_name,
            )
        except ValueError as e:
            return handler_input.response_builder.speak(str(e)).response

        if timer is None or not timer.active:
            speak = f"There's no active feed for {resolved}."
            return handler_input.response_builder.speak(speak).response

        now = time.time()
        elapsed_segment = (now - timer.timerStartTime) if not timer.paused else 0.0
        active_side = getattr(timer, "activeSide", None)
        left = (timer.leftDuration or 0) + (elapsed_segment if active_side == "left" else 0)
        right = (timer.rightDuration or 0) + (elapsed_segment if active_side == "right" else 0)
        total = now - timer.feedStartTime

        total_str = _seconds_to_speech(total)
        left_str = _seconds_to_speech(left)
        right_str = _seconds_to_speech(right)

        if active_side and active_side != "none":
            side_part = f" Currently on the {active_side} breast."
        else:
            side_part = ""

        speak = (
            f"You've been feeding {resolved} for {total_str}.{side_part} "
            f"Left breast: {left_str}. Right breast: {right_str}."
        )

        return handler_input.response_builder.speak(speak).response
