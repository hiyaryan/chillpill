from apis.ext.prompts import system
from apis.ext import openai


class Request:
    def __init__(self, client_name: str, feeling=-1):
        self.client_name = client_name
        self.feeling = feeling
        self.messages = []

    def initiate_chat(self):
        """
        Initiates a chat with the LLM providing it with session context,
        the user's name, the user's feeling, and the initial message.

        Returns the LLM's response.
        """
        self.messages.append(system.get_context())
        self.messages.append(system.initial_message(self.client_name, self.feeling))

        # make a system request to the LLM
        response = openai.get_completion_from_messages(self.messages)

        try:
            response_content = eval(response.choices[0].message["content"])["response"]

        except TypeError:
            response_content = response.choices[0].message["content"]

        return response_content
