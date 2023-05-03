from pynput import keyboard
from collector.choice_reaching import ChoiceReaching
from util.timer import Timer

import time


class KeyboardListener:
    def __init__(self, choice_reaching_collector: ChoiceReaching, timer: Timer):
        self.choice_reaching_collector = choice_reaching_collector
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listening = True
        self.timer = timer

    def on_press(self, key):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            # get the ascii value of the key pressed
            try:
                press = ord(key.char)
            except:
                press = 1

            self.choice_reaching_collector.add_row(data={"press": press})

    def on_release(self, key):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            try:
                release = ord(key.char)
            except:
                release = 1

            self.choice_reaching_collector.add_row(data={"release": release})
