from pynput import mouse


class MouseListener:
    def __init__(self):
        self.listener = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
        )

    def on_move(self, x, y):
        print("Pointer moved to {0}".format((x, y)))

    def on_click(self, x, y, button, pressed):
        print("{0} at {1}".format("Pressed" if pressed else "Released", (x, y)))

    def on_scroll(self, x, y, dx, dy):
        print("Scrolled: {0} as {1}".format("down" if dy < 0 else "up", (x, y)))
