"""Diaper/nappy handler: LogNappyIntent."""

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


class LogNappyIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("LogNappyIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        color = _get_slot_value(handler_input, "color")
        child_name = _get_slot_value(handler_input, "child")

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.log_diaper(uid, mode="both", color=color.lower() if color else None),
                child_name=child_name,
            )
            if color:
                speak = f"Logged a {color} nappy change for {resolved}."
            else:
                speak = f"Logged a nappy change for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response
