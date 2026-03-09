"""Bottle feed handler: LogBottleFeedIntent."""

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


async def _get_last_bottle_amount(api, child_uid: str) -> int | None:
    """Look back 7 days to find the most recent bottle feed amount."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    intervals = await api.list_feed_intervals(
        child_uid,
        start_timestamp=int(start.timestamp()),
        end_timestamp=int(now.timestamp()),
    )
    for interval in sorted(intervals, key=lambda x: x.start, reverse=True):
        if getattr(interval, "mode", None) == "bottle" and getattr(interval, "amount", None):
            return int(interval.amount)
    return None


class LogBottleFeedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("LogBottleFeedIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        amount_str = _get_slot_value(handler_input, "amount")
        child_name = _get_slot_value(handler_input, "child")

        if amount_str:
            try:
                amount = int(float(amount_str))
            except (ValueError, TypeError):
                amount = None
        else:
            amount = None

        if amount is None:
            # Try to fetch the last bottle amount
            try:
                last_amount, resolved = run_huckleberry_with_child(
                    _get_last_bottle_amount,
                    child_name=child_name,
                )
            except ValueError as e:
                return handler_input.response_builder.speak(str(e)).response

            if last_amount is None:
                speak = (
                    "I couldn't find a previous bottle size. Please say the amount — "
                    "for example, log an 80ml bottle feed."
                )
                return (
                    handler_input.response_builder
                    .speak(speak)
                    .ask(speak)
                    .response
                )
            amount = last_amount
        else:
            resolved = None

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.log_bottle(uid, amount=amount),
                child_name=child_name,
            )
            speak = f"Logged a {amount}ml bottle feed for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response
