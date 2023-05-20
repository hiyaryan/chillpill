import flet as ft

from gui.components.chat_message import ChatMessage
from gui.components.message import Message

from apis.request import Request

SESSION_VARIABLES = {}
BOT = "ChillBot"


def get_dialog(page):
    try:
        user_name = SESSION_VARIABLES["user_name"]

    except KeyError:
        page.window_close()

    def close(e):
        page.window_close()

    def join_chat_click(e):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        else:
            # create a new request object and set it to the session
            SESSION_VARIABLES["user_name"] = join_user_name.value
            initiate_session(e)

    def initiate_session(e):
        page.session.set(
            "request",
            Request(
                client_name=SESSION_VARIABLES["user_name"],
                feeling=SESSION_VARIABLES["feeling"],
            ),
        )
        # append the context to the request messages
        page.session.get("request").append_context()

        page.session.set("user_name", SESSION_VARIABLES["user_name"])
        page.dialog.open = False
        page.pubsub.send_all(
            get_system_messages(page.session.get("user_name"), None, "login_message")
        )

    # TODO: Implement on_click for Feedback button.
    if user_name:
        button_options = [
            ft.ElevatedButton(text="Join chat", on_click=initiate_session),
            ft.ElevatedButton(text="Exit", on_click=close),
            # ft.ElevatedButton(text="Feedback", on_click=close),
        ]

        page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text(f"Welcome, {user_name}!", text_align="center"),
            content=ft.Row(controls=button_options, tight=True, alignment="center"),
            actions_alignment="end",
        )

    else:
        # A dialog asking for a user display name
        join_user_name = ft.TextField(
            label="Enter your name to join the chat",
            autofocus=True,
            on_submit=join_chat_click,
        )
        page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Welcome!"),
            content=ft.Column([join_user_name], width=300, height=70, tight=True),
            actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
            actions_alignment="end",
        )


def get_system_messages(user_name, text, message_type):
    """
    System messages are subtext messages appearing in between chat messages to
    inform the user of certain events.
    """

    if message_type == "login_message":
        text = f"{user_name} has entered the chat."

    elif message_type == "offline_message":
        text = f"{BOT} is unable to respond at this time. Please check your connection or close the chat and check back at a later."

    return Message(user_name=user_name, text=text, message_type=message_type)


def get_ft_text(message: Message):
    """
    Get various types of ft.Text objects based on the message type.
    """

    if message.message_type == "chat_message":
        return ChatMessage(message).row

    if message.message_type == "login_message":
        return ft.Text(
            message.text,
            italic=True,
            color=ft.colors.BLACK45,
            size=12,
        )

    elif message.message_type == "offline_message":
        return ft.Text(
            message.text,
            italic=True,
            color=ft.colors.RED,
            size=12,
        )


def main(page: ft.Page):
    page.horizontal_alignment = "stretch"
    page.title = "Chat"

    def send_message_click(e):
        if new_message.value != "":
            # get message and attach the user message to the chat
            message = get_system_messages(
                page.session.get("user_name"), new_message.value, "chat_message"
            )
            page.pubsub.send_all(message)

            # append the user message to the request messages
            page.session.get("request").append_message(
                role="user",
                text=new_message.value,
            )

            # clear the textfield and focus on chat message
            new_message.value = ""
            new_message.focus()

    def request_on_message(message_type):
        """
        A followup function that makes a request to the LLM when a message is
        received from the pubsub.
        """
        response_text = page.session.get("request").make_request(temperature=0.2)
        if response_text:
            if message_type == "login_message":
                # get the login message from the system
                login_text = get_system_messages(BOT, None, "login_message")
                flet_text = get_ft_text(login_text)
                chat.controls.append(flet_text)
                page.update()

                # followup with a chat message
                message_type = "chat_message"

            message = get_system_messages(BOT, response_text, message_type)
        else:
            message = get_system_messages("System", None, "offline_message")

            # pop the user message from the request messages
            page.session.get("request").pop_message()

        flet_text = get_ft_text(message)
        chat.controls.append(flet_text)
        page.update()

    def on_message(message: Message):
        """
        This function is subscribed to the pubsub. Every message submitted by
        the user is followed by a request to the LLM.
        """
        ft_text = get_ft_text(message)
        chat.controls.append(ft_text)
        page.update()

        request_on_message(message.message_type)

    # Subscribe to the pubsub
    page.pubsub.subscribe(on_message)

    # Get a dialog under certain conditions
    get_dialog(page)

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Send a message.",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    # Add everything to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


def launch(**kwargs):
    SESSION_VARIABLES.update(kwargs.get("session_variables", {}))

    print("Launching chat...")
    ft.app(target=main)

    print("Chat closed.")
    return SESSION_VARIABLES
