from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener

import listeners.keyboard as virtual_keyboard

import collector.choice_reaching as cr
from collector.choice_reaching import ChoiceReaching

import util.file as file
import util.console as console

from util.console import ConsoleMenu
from util.timer import Timer

import datetime
import os


usage = """
Usage: sudo python3 main.py

Hotkeys:
    ctrl+q: quit
    ctrl+m: open the main menu
    ctrl+h: print this help message
    ctrl+c: force quit

Menus:
    Main Menu:
        [1] Resume
        [2] Check-in
        [3] Mode
        [4] Config

    Check-in:
        [1] bad
        [2] okay
        [3] neutral
        [4] good
        [5] great

    Mental Modes:
        [1] normal
        [2] focus
        [3] back

    Config Menu:
        [1] Set batch size
        [2] Set idle limit
        [3] Set dataset size
        [4] Back
"""

modes = {}


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
        self.console = ConsoleMenu()

    def run(self):
        print(usage)

        self.start_listeners()
        while True:
            try:
                # check if hotkey is pressed
                if self.keyboard_listener.hotkey in virtual_keyboard.global_hot_keys:
                    # respond to the hotkey
                    if (
                        virtual_keyboard.global_hot_keys[self.keyboard_listener.hotkey]
                        == "quit"
                    ):
                        self.stop_listeners()
                        break

                    else:
                        self.respond_to_hotkey()

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
                    self.activate_window()  # bring the terminal to the front

                    # open the check-in menu
                    feeling = self.console.open_menu("check-in")
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

    def activate_window(self):
        # bring the terminal window to the front using osascript
        if os.name == "posix":
            os.system("osascript -e 'tell application \"Terminal\" to activate'")

    def start_listeners(self):
        self.mouse_listener.listener.start()
        self.keyboard_listener.listener.start()

    def stop_listeners(self):
        self.mouse_listener.listener.stop()
        self.keyboard_listener.listener.stop()

    def toggle_listening(self):
        self.mouse_listener.listening = not self.mouse_listener.listening
        self.keyboard_listener.listening = not self.keyboard_listener.listening

    def respond_to_hotkey(self):
        """
        Respond to the hotkey pressed.
        """

        if (
            virtual_keyboard.global_hot_keys[self.keyboard_listener.hotkey]
            == "main-menu"
        ):
            self.toggle_listening()
            # open the main menu
            choice = self.console.open_menu("main-menu")
            self.console.process_main_menu_choice(self, choice)

            self.keyboard_listener.clear_hotkey()
            self.toggle_listening()

        elif virtual_keyboard.global_hot_keys[self.keyboard_listener.hotkey] == "help":
            # print the usage
            print(usage)
