from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener


class Application:
    def __init__(self):
        self.mouse_listener = MouseListener()
        self.keyboard_listener = KeyboardListener()

    def run(self):
        self.mouse_listener.listener.start()
        self.keyboard_listener.listener.start()

        while True:
            try:
                pass
            except KeyboardInterrupt:
                self.mouse_listener.listener.stop()
                self.keyboard_listener.listener.stop()
                break
