import flet as ft


def main(page: ft.Page):
    page.title = "Chat"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.add()


def launch():
    ft.app(target=main)
