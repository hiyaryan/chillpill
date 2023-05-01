from pynput import keyboard
from collector.choice_reaching import ChoiceReaching


class KeyboardListener:
    def __init__(self, choice_reaching_collector: ChoiceReaching):
        self.choice_reaching_collector = choice_reaching_collector
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )

    def on_press(self, key):
        # get the ascii value of the key pressed
        try:
            press = ord(key.char)
        except:
            press = 1

        self.choice_reaching_collector.add_row(data={"press": press})
        print("Key pressed {0}".format(key))

    def on_release(self, key):
        try:
            release = ord(key.char)
        except:
            release = 1

        self.choice_reaching_collector.add_row(data={"release": release})
        print("Key released {0}".format(key))
