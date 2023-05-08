import os
import openai
import gpt_utils
from ratelimit import completions_with_backoff
from dotenv import load_dotenv


class ChatGPT:
    """
    Represents a chatbot that uses GPT models from openai

    Methods
    -------
    ask_openai()
        Sends user input to the openai api and returns the response
    gpt_text(user_input)
        Interacts with the user, taking their input and displaying the bot's response
    """

    CONVERSATION_LIMIT = 20
    MODEL = "gpt-3.5-turbo"  # gpt-4, gpt-4-0314, gpt-4-32k, gpt-4-32k-0314, gpt-3.5-turbo, gpt-3.5-turbo-0301
    TEMPERATURE = 0.6  # defaults to 1 (0.0 to 2.0)
    MAX_TOKENS = 256  # defaults to  inf
    PRESENCE_PENALTY = 0  # defaults to 0 (-2.0 to 2.0)
    FREQUENCY_PENALTY = 0  # defaults to 0 (-2.0 to 2.0)
    STOP = None  # defaults to None

    def __init__(self) -> None:
        # GPT Setup
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Setup Personality
        self.messages = gpt_utils.setup_personality()

    def ask_openai(self):
        completion = completions_with_backoff(
            model=self.MODEL,
            messages=self.messages,
            temperature=self.TEMPERATURE,
            max_tokens=self.MAX_TOKENS,
            presence_penalty=self.PRESENCE_PENALTY,
            frequency_penalty=self.FREQUENCY_PENALTY,
            stop=self.STOP,
        )
        self.messages.append(completion["choices"][0]["message"])
        return completion["choices"][0]["message"]["content"]

    def gpt_text(self, user_input: str) -> str:
        # Ask user

        self.messages.append({"role": "user", "content": f"{user_input}"})

        # Ask OpenAI
        response = self.ask_openai()

        # Limit conversation while keeping system prompt
        if len(self.messages) >= self.CONVERSATION_LIMIT:
            self.messages[2] = self.messages[0]
            self.messages = self.messages[2:]

        return response
