from pynput import keyboard
from collector.choice_reaching import ChoiceReaching
from util.timer import Timer

import time


global_hot_keys = {
    "<ctrl>+<q>": "quit",
    "<ctrl>+<m>": "main-menu",
    "<ctrl>+<h>": "help",
}


class KeyboardListener:
    def __init__(self, choice_reaching_collector: ChoiceReaching, timer: Timer):
        self.choice_reaching_collector = choice_reaching_collector
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listening = True
        self.timer = timer
        self.hotkey = ""

    def start_hotkey(self):
        self.hotkey = "<ctrl>"

    def set_hotkey(self, key):
        self.hotkey = self.hotkey + "+<" + key + ">"

    def clear_hotkey(self):
        self.hotkey = ""

    def on_press(self, key):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            # get the ascii value of the key pressed
            try:
                # if ctrl is pressed then the next key pressed is the hotkey
                if self.hotkey == "<ctrl>":
                    self.set_hotkey(key.char)

                press = ord(key.char)
            except:
                if key == keyboard.Key.ctrl:
                    self.start_hotkey()

                press = 1

            self.choice_reaching_collector.add_row(data={"press": press})

    def on_release(self, key):
        if self.listening:
            self.timer.last_active_time = time.time_ns()
            try:
                release = ord(key.char)
            except:
                # if ctrl is released then the hotkey is cleared
                if key == keyboard.Key.ctrl:
                    self.clear_hotkey()

                release = 1

            self.choice_reaching_collector.add_row(data={"release": release})
