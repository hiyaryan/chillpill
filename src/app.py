from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener
from collector.choice_reaching import ChoiceReaching

import util
import datetime


class Application:
    def __init__(self):
        self.choice_reaching_collector = ChoiceReaching()
        self.mouse_listener = MouseListener(self.choice_reaching_collector)
        self.keyboard_listener = KeyboardListener(self.choice_reaching_collector)

    def run(self):
        self.mouse_listener.listener.start()
        self.keyboard_listener.listener.start()

        while True:
            try:
                if len(self.choice_reaching_collector.dataset) > 1000000:
                    util.write_tracking_file(
                        datetime.datetime.now().strftime("%Y%m%d-%H%M%S" + ".csv"),
                        self.choice_reaching_collector.dataset,
                    )

                    self.choice_reaching_collector.reset()

            except KeyboardInterrupt:
                self.mouse_listener.listener.stop()
                self.keyboard_listener.listener.stop()
                break
