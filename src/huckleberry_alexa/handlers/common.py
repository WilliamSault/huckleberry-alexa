"""Common Alexa handlers: Launch, Help, Stop, Cancel, SessionEnded, CatchAll."""

from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak = (
            "Welcome to Huckleberry. You can log a feed, a nappy change, or ask "
            "for the last feed status. What would you like to do?"
        )
        return (
            handler_input.response_builder
            .speak(speak)
            .ask(speak)
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak = (
            "You can say: start a feed on my left breast, log a nappy change, "
            "log a bottle feed, pause the feed, stop the feed, "
            "how long ago was the last feed, or when was the last nappy change."
        )
        return (
            handler_input.response_builder
            .speak(speak)
            .ask("What would you like to do?")
            .response
        )


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            is_intent_name("AMAZON.CancelIntent")(handler_input)
            or is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        return (
            handler_input.response_builder
            .speak("Goodbye!")
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        print(f"Encountered exception: {exception}", flush=True)
        speak = "Sorry, I had trouble doing what you asked. Please try again."
        return (
            handler_input.response_builder
            .speak(speak)
            .ask(speak)
            .response
        )
