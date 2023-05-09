import flet as ft


class Message:
    def __init__(self, user, text):
        self.user = user
        self.text = text


def main(page: ft.Page):
    page.title = "Chat"

    chat = ft.Column()
    new_message = ft.TextField()

    def on_message(message: Message):
        chat.controls.append(ft.Text(f"Me: {message.text}"))
        page.update()

    def send_click(e):
        on_message(Message(page.session_id, new_message.value))
        new_message.value = ""
        page.update()

    page.add(
        chat,
        ft.Row(controls=[new_message, ft.ElevatedButton("Send", on_click=send_click)]),
    )


def launch():
    ft.app("chat", target=main)
