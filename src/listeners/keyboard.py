from pynput import keyboard


class KeyboardListener:
    def __init__(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )

    def on_press(self, key):
        print("Key pressed {0}".format(key))

    def on_release(self, key):
        print("Key released {0}".format(key))
