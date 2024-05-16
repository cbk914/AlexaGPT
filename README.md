# Alexa GPT Multilingual Assistant

## Description

Alexa GPT Multilingual Assistant is an Alexa skill that leverages OpenAI's GPT-4 to provide conversational AI capabilities in multiple languages. The skill allows users to ask questions or request information, and it responds appropriately in the user's language. This project demonstrates how to build a multilingual Alexa skill using a single interaction model and dynamically handling language-specific responses.

## Installation

### Prerequisites
- An Amazon Developer account.
- AWS account for deploying the Lambda function.
- OpenAI API key.

### Steps
1. **Clone the Repository**
   ```sh
   git clone https://github.com/cbk914/AlexaGPT.git
   cd AlexaGPT

2. **Set Up AWS Lambda**

- Create a new Lambda function in the AWS Management Console.
- Set the runtime to Python 3.9.
- Add environment variables:
  * OPENAI_API_KEY with your OpenAI API key.
- Upload the lambda_function.zip package or deploy using the AWS CLI.

3. **Configure AWS Secrets Manager (Optional)**

- Store your OpenAI API key in AWS Secrets Manager for added security.
- Grant your Lambda function access to the secret.

4. **Create Alexa Skill**

- Go to the Alexa Developer Console.
- Create a new skill and select "Custom" model.
- Add languages you want to support (e.g., English and Spanish).
- Configure the interaction model using the provided interaction_model.json.

5. **Link Lambda Function**

- In the Alexa Developer Console, under "Endpoint", select "AWS Lambda ARN" and enter the ARN of your Lambda function.

## Usage

1. Invocation

- Invoke the skill using the configured invocation name (e.g., "assistant gpt").
- Example commands:
  - "Ask assistant gpt what is the weather today?"
  - "Ask assistant gpt to tell me about the Eiffel Tower."
  - "Ask assistant gpt qué es inteligencia artificial."

2. Intents

- GptQueryIntent: Ask any question.
- GreetingIntent: Say hello.
- FarewellIntent: Say goodbye.
- AMAZON.HelpIntent: Get help information.
- AMAZON.CancelIntent: Cancel the current action.
- AMAZON.StopIntent: Stop the skill.

## Disclaimer
This project is for demonstration purposes only. The author is not affiliated with OpenAI or Amazon. All product names, logos, and brands are property of their respective owners. Use of these names, logos, and brands does not imply endorsement.

## License
This project is licensed under the GPL 3 License. See the LICENSE file for more details.

By using this project, you agree to the terms and conditions of the licenses associated with the dependencies used in this project.

## Contact
For any questions or support, please open an issue on the GitHub repository.
