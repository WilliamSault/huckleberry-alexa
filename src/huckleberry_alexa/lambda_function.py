"""AWS Lambda entry point for the Huckleberry Alexa skill."""

from ask_sdk_core.skill_builder import SkillBuilder

from huckleberry_alexa.handlers.common import (
    LaunchRequestHandler,
    HelpIntentHandler,
    CancelAndStopIntentHandler,
    SessionEndedRequestHandler,
    CatchAllExceptionHandler,
)
from huckleberry_alexa.handlers.nursing import (
    StartNursingIntentHandler,
    PauseNursingIntentHandler,
    SwitchBreastIntentHandler,
    StopNursingIntentHandler,
)
from huckleberry_alexa.handlers.diaper import LogNappyIntentHandler
from huckleberry_alexa.handlers.bottle import LogBottleFeedIntentHandler
from huckleberry_alexa.handlers.status import (
    LastFeedStatusIntentHandler,
    LastNappyStatusIntentHandler,
    CurrentFeedStatusIntentHandler,
)

sb = SkillBuilder()

# Register handlers in priority order
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(StartNursingIntentHandler())
sb.add_request_handler(PauseNursingIntentHandler())
sb.add_request_handler(SwitchBreastIntentHandler())
sb.add_request_handler(StopNursingIntentHandler())
sb.add_request_handler(LogNappyIntentHandler())
sb.add_request_handler(LogBottleFeedIntentHandler())
sb.add_request_handler(LastFeedStatusIntentHandler())
sb.add_request_handler(LastNappyStatusIntentHandler())
sb.add_request_handler(CurrentFeedStatusIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
