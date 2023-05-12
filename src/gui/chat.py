import flet as ft

from gui.components.chat_message import ChatMessage
from gui.components.message import Message

from apis.request import Request

SESSION_VARIABLES = {}


def main(page: ft.Page):
    page.horizontal_alignment = "stretch"
    page.title = "Chat"

    def join_chat_click(e):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        else:
            page.session.set(
                "request",
                Request(
                    client_name=join_user_name.value,
                    feeling=SESSION_VARIABLES["feeling"],
                ),
            )
            SESSION_VARIABLES["user_name"] = join_user_name.value
            page.session.set("user_name", join_user_name.value)
            page.dialog.open = False
            page.pubsub.send_all(
                Message(
                    user_name="bot",
                    text="ChillBot has entered the chat.",
                    message_type="login_message",
                )
            )
            page.pubsub.send_all(
                Message(
                    user_name=page.session.get("user_name"),
                    text="You have entered the chat.",
                    message_type="login_message",
                )
            )
            page.update()

    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(
                Message(
                    user_name=page.session.get("user_name"),
                    text=new_message.value,
                    message_type="chat_message",
                )
            )

            page.session.get("request").append_message(
                role="user",
                text=new_message.value,
            )
            new_message.value = ""
            new_message.focus()

            text = page.session.get("request").make_request(temperature=0.5)
            if not text:
                user_name = "Admin"
                message_type = "admin_message"
                text = "ChillBot is unable to respond at this time. Please close the chat and check back at a later."
            else:
                user_name = "ChillBot"
                message_type = "chat_message"

            page.pubsub.send_all(
                Message(
                    user_name=user_name,
                    text=text,
                    message_type=message_type,
                )
            )

            page.session.get("request").append_message(
                role="assistant",
                text=text,
            )

            page.update()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message.row)

        elif message.message_type == "login_message":
            m = ft.Text(
                message.text,
                italic=True,
                color=ft.colors.BLACK45,
                size=12,
            )
            chat.controls.append(m)

            if message.user_name == "bot":
                page.session.get("request").append_context()
                response = page.session.get("request").make_request(temperature=0.2)

                m = Message(
                    user_name="ChillBot",
                    text=response,
                    message_type="login_message",
                )

                chat_message = ChatMessage(m)
                chat.controls.append(chat_message.row)

        elif message.message_type == "admin_message":
            m = ft.Text(
                message.text,
                italic=True,
                color=ft.colors.RED,
                size=12,
            )
            chat.controls.append(m)

        page.update()

    page.pubsub.subscribe(on_message)

    # TODO: Only open dialog if user_name is not set. Initially, user_name is set to None until first chat session is closed. This is set in app.py.

    # When the user_name is set, ChillBot should still send the first message and there should chat messages "__user_name__ has entered the chat." should still be sent.

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
