from apis.ext.prompts import system
from apis.ext.prompts import assistant

from apis.ext import openai
from urllib3 import request


class Request:
    def __init__(self, client_name: str, feeling=-1):
        self.client_name = client_name
        self.feeling = feeling
        self.messages = []

    def make_request(self, attempt=1, temperature=0):
        """
        Takes this array of messages and makes a request to the LLM. Returns
        the content of the response. If any errors are made when parsing the
        response, the LLM will be requested to correct its response providing
        the LLM with time to think.

        Returns the response if the response is correct, otherwise, returns
        None.
        """
        # check for internet connection
        try:
            request.urlopen("http://142.251.46.206", timeout=1)
        except:
            print("No internet connection.")
            return None

        # return None if the LLM is unable to correctly respond in 3 attempts.
        if attempt > 3:
            return None

        # make a system request to the LLM
        response = openai.get_completion_from_messages(
            self.messages, temperature=temperature
        )

        print(response)
        response_content = response.choices[0].message["content"]

        try:
            response = eval(response_content)["response"]
            self.append_message(role="assistant", text=response_content)

            print(self.messages)
            return response

        except TypeError:
            print("TypeError: Assistant did not format response correctly.")
            print(f"[Attempt {attempt + 1}] Re-requesting...")
            self.messages.append(system.get_type_error_prompt())
            self.make_request(attempt=attempt + 1, temperature=temperature)

        except SyntaxError:
            print("SyntaxError: Assistant entered incorrect value.")
            print(f"[Attempt {attempt + 1}] Re-requesting...")
            self.messages.append(system.get_syntax_error_prompt())
            self.make_request(attempt=attempt + 1, temperature=temperature)

    def append_message(self, role, text):
        """
        Appends message to this array of messages to provide conversational
        history to LLM.
        """
        # TODO: This may be a good spot to filter through the messages and send on the most recent messages or a summary of the conversation written by the LLM
        self.messages.append(system.get_message(role, text))

    def append_context(self):
        """
        Appends the initial set of messages to this array to provide the LLM
        with context on how the user is currently feeling and instructions.
        """
        self.messages.append(assistant.get_job_description())
        self.messages.append(assistant.get_format_instructions())
        self.messages.append(system.get_initial_prompt(self.client_name, self.feeling))
