import re
import os

from ec2 import get_service_status, set_service_status, set_autoscaling_instances
from cloudwatch import get_billing


def handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            os.environ.get('ALEXA_SKILL_ID')):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


def on_session_started(session_started_request, session):
    print("Starting new session.")


def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    card_title = "Alexa Cloud Control"
    session_attributes = {}
    reprompt_text = ""
    should_end_session = True

    if intent_name == "GetServices":
        speech_output = get_service_status(intent["slots"])

        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    elif intent_name == "ManageServices":
        speech_output = set_service_status(intent["slots"])

        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    elif intent_name == "ScaleServices":
        speech_output = set_autoscaling_instances(intent["slots"])

        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    elif intent_name == "GetBilling":
        speech_output = get_billing()

        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()

    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()

    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("Ending session.")
    # Cleanup goes here...


def handle_session_end_request():
    card_title = "Alexa Cloud Control"
    speech_output = "Thank you for using the Alexa Cloud Control skill. See you next time!"
    should_end_session = True

    speech_output = '<speak>' + speech_output + '</speak>'

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


def get_welcome_response():
    session_attributes = {}
    card_title = "Alexa Cloud Control"
    speech_output = "Welcome to the Alexa cloud control skill. " \
                    "You can ask me for server status, " \
                    "ask me to turn servers on or off, " \
                    "ask me for your amazon bill, or" \
                    "scale a autoscaling group for you."
    reprompt_text = "Please give me a purpose, " \
                    "for example 'how many development servers are running'."
    should_end_session = False

    speech_output = '<speak>' + speech_output + '</speak>'

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    # Strip any SSML from card output
    regex = re.compile(r"\<[^>]*\>")
    card_output = re.sub(regex, '', output)

    return {
        "outputSpeech": {
            "type": "SSML",
            "ssml": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": card_output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
