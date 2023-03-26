import os
import openai

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OpenAI API key. Set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

def lambda_handler(event, context):
    input_text = event["request"]["intent"]["slots"]["text"]["value"]
    
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=input_text,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5,
    )
    
    output_text = response.choices[0].text.strip()
    
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": output_text
            },
            "shouldEndSession": False
        }
    }
