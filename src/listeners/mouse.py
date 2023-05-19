from pynput import mouse
from collector.choice_reaching import ChoiceReaching
from util.timer import Timer

import time


class MouseListener:
    def __init__(self, choice_reaching_collector: ChoiceReaching, timer: Timer):
        self.choice_reaching_collector = choice_reaching_collector
        self.listener = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
        )
        self.listening = True
        self.timer = timer

    def on_move(self, x, y):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            self.choice_reaching_collector.add_row(
                data={"input_type": 1, "x": x, "y": y}
            )

    def on_click(self, x, y, button, pressed):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            if pressed:
                self.choice_reaching_collector.add_row(
                    data={"input_type": 2, "press": 1}
                )
            else:
                self.choice_reaching_collector.add_row(
                    data={"input_type": 2, "release": 1}
                )

    def on_scroll(self, x, y, dx, dy):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            self.choice_reaching_collector.add_row(data={"input_type": 4, "scroll": 1})
