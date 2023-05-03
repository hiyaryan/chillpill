from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener

import collector.choice_reaching as cr
from collector.choice_reaching import ChoiceReaching

import util.file as file
from util.console import ConsoleMenu
from util.timer import Timer

import datetime


class Application:
    def __init__(self):
        self.timer = Timer()

        self.feeling_selected = False

        # initialize the collector
        self.choice_reaching_collector = ChoiceReaching()

        # initialize the listeners for mouse and keyboard
        self.mouse_listener = MouseListener(self.choice_reaching_collector, self.timer)
        self.keyboard_listener = KeyboardListener(
            self.choice_reaching_collector, self.timer
        )

        # initialize the menu
        self.menu = ConsoleMenu(
            title="How are you feeling?",
            options=["[1] bad", "[2] okay", "[3] neutral", "[4] good", "[5] great"],
        )

    def run(self):
        self.start_listeners()

        while True:
            try:
                # write the data to a file every 100,000 samples
                if len(self.choice_reaching_collector.dataset) >= file.MAX_DATASET_SIZE:
                    file.write_tracking_file(
                        datetime.datetime.now().strftime("%Y%m%d-%H%M%S" + ".csv"),
                        self.choice_reaching_collector.dataset,
                    )

                    print("Dataset written to file.")
                    self.choice_reaching_collector.reset_batch()
                    self.choice_reaching_collector.reset_dataset()

                # ask the user how they are feeling every 2500 samples
                elif (
                    not self.feeling_selected
                    and len(self.choice_reaching_collector.batch) % cr.MAX_BATCH_SIZE
                    == 0
                ):
                    self.feeling_selected = True
                    self.toggle_listening()

                    feeling = self.menu.run().chosen_menu_index
                    self.choice_reaching_collector.set_feeling(feeling)
                    self.choice_reaching_collector.add_batch()
                    self.choice_reaching_collector.reset_batch()

                    print(
                        f"Dataset length {len(self.choice_reaching_collector.dataset)}/{file.MAX_DATASET_SIZE}"
                    )
                    self.toggle_listening()

                # reset the feeling selected flag
                elif (
                    self.feeling_selected
                    and len(self.choice_reaching_collector.batch) % cr.MAX_BATCH_SIZE
                    != 0
                ):
                    self.feeling_selected = False

                # calculate the idle time
                if (
                    self.timer.greater_than_idle_limit()
                    and len(self.choice_reaching_collector.batch) > 0
                ):
                    print("Idle limit reached. Batch has been reset.")
                    print(
                        f"Dataset length {len(self.choice_reaching_collector.dataset)}/{file.MAX_DATASET_SIZE}"
                    )
                    self.choice_reaching_collector.reset_batch()

            except KeyboardInterrupt:
                self.stop_listeners()
                break

    def start_listeners(self):
        self.mouse_listener.listener.start()
        self.keyboard_listener.listener.start()

    def stop_listeners(self):
        self.mouse_listener.listener.stop()
        self.keyboard_listener.listener.stop()

    def toggle_listening(self):
        self.mouse_listener.listening = not self.mouse_listener.listening
        self.keyboard_listener.listening = not self.keyboard_listener.listening
