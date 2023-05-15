def get_message(role, text):
    return {
        "role": role,
        "content": text,
    }


def get_initial_prompt(name, feeling):
    message = f"""
A new client named {name}, has entered the chat with a feeling of \
{feeling}. Greet the client. \
"""

    return {
        "role": "system",
        "content": message,
    }


def get_user_message_in_system_message(name, text):
    message = f"""
Respond to {name}'s message, \
```
{text}
``` 
"""
    return {
        "role": "system",
        "content": message,
    }


def get_type_error_prompt():
    message = f"""
Your response must be in JSON format.
"""
    return {
        "role": "system",
        "content": message,
    }


def get_syntax_error_prompt():
    message = f"""
Your response must follow exactly as described in the description of the keys 
of the required JSON format.    
"""
    return {
        "role": "system",
        "content": message,
    }
