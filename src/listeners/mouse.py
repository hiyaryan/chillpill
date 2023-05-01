from pynput import mouse
from collector.choice_reaching import ChoiceReaching


class MouseListener:
    def __init__(self, choice_reaching_collector: ChoiceReaching):
        self.choice_reaching_collector = choice_reaching_collector
        self.listener = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
        )

    def on_move(self, x, y):
        self.choice_reaching_collector.add_row(data={"x": x, "y": y})
        print("Pointer moved to {0}".format((x, y)))

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.choice_reaching_collector.add_row(data={"press": 1})
        else:
            self.choice_reaching_collector.add_row(data={"release": 1})

        print(button.value)
        print("{0} at {1}".format("Pressed" if pressed else "Released", (x, y)))

    def on_scroll(self, x, y, dx, dy):
        self.choice_reaching_collector.add_row(data={"scroll": 1})

        print("Scrolled: {0} as {1}".format("down" if dy < 0 else "up", (x, y)))
