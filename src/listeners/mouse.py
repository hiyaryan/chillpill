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
            self.choice_reaching_collector.add_row(data={"x": x, "y": y})

    def on_click(self, x, y, button, pressed):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            if pressed:
                self.choice_reaching_collector.add_row(data={"press": 1})
            else:
                self.choice_reaching_collector.add_row(data={"release": 1})

    def on_scroll(self, x, y, dx, dy):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            self.choice_reaching_collector.add_row(data={"scroll": 1})
