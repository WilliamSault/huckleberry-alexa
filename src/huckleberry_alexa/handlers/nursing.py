"""Nursing handlers: Start, Pause, Switch, Stop."""

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


class StartNursingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("StartNursingIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        side = _get_slot_value(handler_input, "side")
        child_name = _get_slot_value(handler_input, "child")

        if not side:
            return (
                handler_input.response_builder
                .speak("Which side? Left or right?")
                .ask("Please say left or right.")
                .response
            )

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.start_nursing(uid, side=side.lower()),
                child_name=child_name,
            )
            speak = f"Started a {side} breast feed for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response


class PauseNursingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("PauseNursingIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        child_name = _get_slot_value(handler_input, "child")

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.pause_nursing(uid),
                child_name=child_name,
            )
            speak = f"Feed paused for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response


class SwitchBreastIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("SwitchBreastIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        child_name = _get_slot_value(handler_input, "child")

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.switch_nursing_side(uid),
                child_name=child_name,
            )
            speak = f"Switched breast for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response


class StopNursingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("StopNursingIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        child_name = _get_slot_value(handler_input, "child")

        try:
            _, resolved = run_huckleberry_with_child(
                lambda api, uid: api.complete_nursing(uid),
                child_name=child_name,
            )
            speak = f"Feed saved for {resolved}."
        except ValueError as e:
            speak = str(e)

        return handler_input.response_builder.speak(speak).response
