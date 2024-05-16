import os
import json
import logging
import openai
import boto3
from botocore.exceptions import ClientError
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response
from ask_sdk_model.interfaces.display import RenderTemplateDirective, BodyTemplate1
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize Boto3 client for Secrets Manager
secrets_client = boto3.client('secretsmanager')

def get_secret(secret_name):
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        logger.error(f"Error retrieving secret: {e}")
        return None

# Retrieve the OpenAI API key from Secrets Manager
openai_api_key = get_secret('openai/api_key')
openai.api_key = openai_api_key if openai_api_key else os.getenv('OPENAI_API_KEY')

cloudwatch = boto3.client('cloudwatch')

def log_interaction(locale):
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': 'UserInteractions',
                'Dimensions': [
                    {
                        'Name': 'SkillName',
                        'Value': 'Assistant GPT'
                    },
                    {
                        'Name': 'Locale',
                        'Value': locale
                    }
                ],
                'Value': 1,
                'Unit': 'Count'
            },
        ],
        Namespace='AlexaSkill'
    )

def get_response_by_locale(locale, key):
    responses = {
        'en-US': {
            'WELCOME': 'Welcome to GPT-4 chat. How can I assist you today?',
            'HELP': 'You can ask me any question and I will try to provide an answer. For example, you can say "Tell me about the Eiffel Tower". How can I help you?',
            'GOODBYE': 'Goodbye! Have a great day!',
            'ERROR': 'Sorry, I had trouble doing what you asked. Please try again.',
            'ANYTHING_ELSE': 'Anything else?'
        },
        'es-ES': {
            'WELCOME': 'Bienvenido al asistente GPT-4. ¿Cómo puedo ayudarte hoy?',
            'HELP': 'Puedes preguntarme cualquier cosa y trataré de darte una respuesta. Por ejemplo, puedes decir "Háblame sobre la Torre Eiffel". ¿En qué puedo ayudarte?',
            'GOODBYE': '¡Adiós! ¡Que tengas un buen día!',
            'ERROR': 'Lo siento, tuve problemas para hacer lo que pediste. Por favor intenta de nuevo.',
            'ANYTHING_ELSE': '¿Algo más?'
        }
    }
    return responses.get(locale, {}).get(key, responses['en-US'][key])

def generate_gpt_response(locale, chat_history, new_question):
    prompt_prefix = {
        'en-US': "You are a helpful assistant.",
        'es-ES': "Tú eres un asistente útil. Responde en español."
    }
    prompt = f"{prompt_prefix.get(locale, prompt_prefix['en-US'])} {new_question}"
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["chat_history"] = []
        speak_output = get_response_by_locale(locale, 'WELCOME')
        if handler_input.request_envelope.context.system.device.supported_interfaces.alexa_presentation_apl:
            handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title="Assistant GPT-4",
                        text_content={
                            "primaryText": {
                                "text": speak_output,
                                "type": "PlainText"
                            }
                        }
                    )
                )
            )
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class GptQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        query = handler_input.request_envelope.request.intent.slots["query"].value
        session_attr = handler_input.attributes_manager.session_attributes
        chat_history = session_attr.get("chat_history", [])
        response = generate_gpt_response(locale, chat_history, query)
        chat_history.append((query, response))
        session_attr["chat_history"] = chat_history
        handler_input.attributes_manager.session_attributes = session_attr

        log_interaction(locale)

        return handler_input.response_builder.speak(response).ask(get_response_by_locale(locale, 'ANYTHING_ELSE')).response

class GreetingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GreetingIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        speak_output = get_response_by_locale(locale, 'WELCOME')
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class FarewellIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("FarewellIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        speak_output = get_response_by_locale(locale, 'GOODBYE')
        return handler_input.response_builder.speak(speak_output).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        locale = handler_input.request_envelope.request.locale
        logger.error(exception, exc_info=True)
        speak_output = get_response_by_locale(locale, 'ERROR')
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        speak_output = get_response_by_locale(locale, 'HELP')
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or 
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        speak_output = get_response_by_locale(locale, 'GOODBYE')
        return handler_input.response_builder.speak(speak_output).response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        speak_output = get_response_by_locale(locale, 'ERROR')
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(GreetingIntentHandler())
sb.add_request_handler(FarewellIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
