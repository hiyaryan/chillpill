from pynput import mouse
from collectors.tracking import TrackingCollector
from util.timer import Timer

import time


class MouseListener:
    def __init__(self, tracking_collector: TrackingCollector, timer: Timer):
        self.tracking_collector = tracking_collector
        self.listener = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
        )
        self.listening = True
        self.timer = timer

    def on_move(self, x, y):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            self.tracking_collector.add_row(data={"input_type": 1, "x": x, "y": y})

    def on_click(self, x, y, button, pressed):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            if pressed:
                self.tracking_collector.add_row(data={"input_type": 2, "press": 1})
            else:
                self.tracking_collector.add_row(data={"input_type": 2, "release": 1})

    def on_scroll(self, x, y, dx, dy):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            self.tracking_collector.add_row(data={"input_type": 4, "scroll": 1})
