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
        nappy_type = _get_slot_value(handler_input, "nappy_type")
        child_name = _get_slot_value(handler_input, "child")

        _TYPE_TO_MODE = {
            "pee": "pee",
            "wet": "pee",
            "poo": "poo",
            "poop": "poo",
            "dirty": "poo",
            "both": "both",
            "mixed": "both",
        }
        mode = _TYPE_TO_MODE.get(nappy_type.lower(), "both") if nappy_type else "both"
        poo_color = color.lower() if color and mode in ("poo", "both") else None

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.log_diaper(uid, mode=mode, color=poo_color),
                child_name=child_name,
            )
            type_word = nappy_type if nappy_type else "nappy"
            if poo_color:
                speak = f"Logged a {poo_color} {type_word} change for {resolved}."
            else:
                speak = f"Logged a {type_word} change for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response
