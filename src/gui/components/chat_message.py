import flet as ft

from gui.components.message import Message


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.row = ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(message.user_name),
                    color=ft.colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                ft.Text(message.text, selectable=True),
            ],
            wrap=True,
        )

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]
