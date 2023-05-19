from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener

import listeners.keyboard as virtual_keyboard

from collectors.tracking import TrackingCollector

import util.file as file_util
import util.constants as constants
import util.console as console
import util.timer as timer

from util.console import ConsoleMenu
from util.timer import Timer

import datetime
import os

from gui import chat


usage = """
Usage: sudo python3 main.py

Hotkeys:
    ctrl+q: quit
    ctrl+m: open the main menu
    ctrl+h: print this help message
    ctrl+c: force quit
    ctrl+o: open the chat

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
        [3] custom
        [4] back

    Config Menu:
        [1] Set batch size
        [2] Set idle limit
        [3] Set dataset size
        [4] Back
"""

config_usage = """
Configurations:
    batch size: set the number of tracking instances per trial
    idle limit: set the allowable idle minutes before a trial is reset
    dataset size: set the number of trials per dataset
"""

modes = {
    "normal": {
        "MAX_BATCH_SIZE": 5000,
        "IDLE_LIMIT": 10 * 60 * 1e9,
        "MAX_DATASET_SIZE": 5e4,
    },
    "focus": {
        "MAX_BATCH_SIZE": 10000,
        "IDLE_LIMIT": 5 * 60 * 1e9,
        "MAX_DATASET_SIZE": 1e5,
    },
    "custom": {
        "MAX_BATCH_SIZE": 0,
        "IDLE_LIMIT": 0,
        "MAX_DATASET_SIZE": 0,
    },
}


# TODO: This class is getting too big, needs some refactoring. Move static methods to a separate utility file. Maybe move the menu/hotkey logic to a separate file as well. Needs some cleanup and more documentation also.
class App:
    def __init__(self):
        print(usage)

        # user name set on chat launch
        self.user_name = None

        # TODO: Move timer into tracking collector
        self.timer = Timer()

        # initialize the collector
        # if a saved shot exists, load it
        if os.path.exists(file_util.get_saved_shot_path("wip.json")):
            print("`wip.json` file found. Resuming progress...")

            # load the WIP file
            saved_shot = file_util.load_saved_shot_file("wip.json")

            # initialize the collector with the contents of the WIP file
            self.tracking_collector = TrackingCollector(
                saved_shot["dataset"], saved_shot["config"]["batch_size"]
            )

            self.tracking_collector.max_dataset_size = saved_shot["config"][
                "dataset_size"
            ]
            self.tracking_collector.max_batch_size = saved_shot["config"]["batch_size"]

            self.timer.idle_limit = saved_shot["config"]["idle_limit"]

            print(
                f"""
Configuration loaded:
    Dataset size: {self.tracking_collector.max_dataset_size / self.tracking_collector.max_batch_size} batches, {self.tracking_collector.max_dataset_size} samples
    Batch size: {self.tracking_collector.max_batch_size} samples
    Idle limit: {self.timer.idle_limit / 60 / 1e9} minutes\n"""
            )

        # otherwise, initialize the collector with a new dataset
        else:
            print("No `wip.json` file found. Initializing new dataset...\n")
            self.tracking_collector = TrackingCollector()

        # initialize the listeners for mouse and keyboard
        self.mouse_listener = MouseListener(self.tracking_collector, self.timer)

        self.keyboard_listener = KeyboardListener(self.tracking_collector, self.timer)

        # initialize the menu
        self.console = ConsoleMenu()

    def run(self):
        # start listeners but do not listen for input until both are ready
        self.toggle_listening()
        self.start_listeners()
        self.toggle_listening()

        while True:
            try:
                # check if hotkey is pressed
                if self.keyboard_listener.hotkey in virtual_keyboard.global_hot_keys:
                    # respond to the hotkey
                    self.respond_to_hotkey()

                # write the entire dataset to a file every n samples
                if (
                    len(self.tracking_collector.dataset)
                    >= self.tracking_collector.max_dataset_size
                ):
                    file_util.write_tracking_file(
                        datetime.datetime.now().strftime("%Y%m%d-%H%M%S" + ".csv"),
                        self.tracking_collector.dataset,
                    )

                    print("Dataset written to file.")
                    self.tracking_collector.reset_batch()
                    self.tracking_collector.reset_dataset()

                    # remove the saved shot if it exists
                    if os.path.exists(file_util.get_saved_shot_path("wip.json")):
                        os.remove(file_util.get_saved_shot_path("wip.json"))

                # ask the user how they are feeling every n samples
                elif (
                    len(self.tracking_collector.batch)
                    >= self.tracking_collector.max_batch_size
                ):
                    self.toggle_listening()
                    self.activate_window()  # bring the terminal to the front

                    # open the check-in menu and set the current feeling
                    check_in_choice = self.get_choice_from_menu("check-in")
                    self.tracking_collector.set_feeling(check_in_choice)
                    self.tracking_collector.add_batch()
                    self.tracking_collector.reset_batch()

                    print(
                        f"Dataset length {len(self.tracking_collector.dataset)}/{self.tracking_collector.max_dataset_size}"
                    )
                    self.toggle_listening()

                # calculate the idle time
                if (
                    self.timer.greater_than_idle_limit()
                    and len(self.tracking_collector.batch) > 0
                ):
                    print("Idle limit reached. Batch has been reset.")
                    print(
                        f"Dataset length {len(self.tracking_collector.dataset)}/{self.tracking_collector.max_dataset_size}"
                    )
                    self.tracking_collector.reset_batch()

            except KeyboardInterrupt:
                self.stop_listeners()
                break

    def quit(self):
        self.stop_listeners()

        if (
            len(self.tracking_collector.dataset)
            / self.tracking_collector.min_batch_size
            > 1
        ):
            # TODO: Write a function in file to update the saved shot template for App
            file_util.SAVED_SHOT_TEMPLATE["config"] = {
                "dataset_size": self.tracking_collector.max_dataset_size,
                "batch_size": self.tracking_collector.max_batch_size,
                "idle_limit": self.timer.idle_limit,
            }
            file_util.SAVED_SHOT_TEMPLATE["dataset"] = self.tracking_collector.dataset

            file_util.write_saved_shot_file(
                datetime.datetime.now().strftime("wip" + ".json"),
                file_util.SAVED_SHOT_TEMPLATE,
            )

            print("\nProgress saved.")

        exit()

    def activate_window(self):
        # bring the terminal window to the front using osascript
        if os.name == "posix":
            os.system("osascript -e 'tell application \"Terminal\" to activate'")

    def start_listeners(self):
        """
        Start and wait for the listeners to become ready.
        """
        self.mouse_listener.listener.start()
        self.mouse_listener.listener.wait()

        self.keyboard_listener.listener.start()
        self.keyboard_listener.listener.wait()

    def stop_listeners(self):
        """
        Stop the listeners.
        """
        self.mouse_listener.listener.stop()
        self.keyboard_listener.listener.stop()

    def toggle_listening(self):
        """
        Toggle the listening flags to resume or pause listening.
        """
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

            # keep main menu open until the user quits
            main_menu_exit = False
            while not main_menu_exit:
                # open the main menu
                main_menu_choice = self.get_choice_from_menu("main-menu")

                # get and execute the action from the main menu
                action = self.console.process_main_menu_choice(self, main_menu_choice)
                main_menu_exit = self.execute_main_menu_choice(main_menu_choice, action)

            self.keyboard_listener.clear_hotkey()
            self.toggle_listening()

        elif virtual_keyboard.global_hot_keys[self.keyboard_listener.hotkey] == "help":
            print(usage)

        elif virtual_keyboard.global_hot_keys[self.keyboard_listener.hotkey] == "quit":
            self.quit()

        elif virtual_keyboard.global_hot_keys[self.keyboard_listener.hotkey] == "chat":
            chat_session_variables = chat.launch(
                session_variables={
                    "feeling": self.tracking_collector.feeling,
                    "user_name": self.user_name,
                }
            )

            if not self.user_name:
                self.user_name = chat_session_variables["user_name"]
                print(f"User name set to {self.user_name}.")

    def get_choice_from_menu(self, terminal_menu):
        """
        Get a chosen menu index from a terminal menu.
        """
        choice = None
        while choice == None:
            choice = (
                self.console.get_terminal_menu(terminal_menu).run().chosen_menu_index
            )

        return choice

    def execute_main_menu_choice(self, choice, action):
        """
        Execute the main menu choice.
        """
        match console.menus["main-menu"]["options"][choice]:
            case "[2] Check-in":
                check_in_choice = None
                while check_in_choice == None:
                    check_in_choice = action[choice]().chosen_menu_index

                self.tracking_collector.set_feeling(check_in_choice)

                # add batch to dataset if it has the minimum size
                if (
                    len(self.tracking_collector.batch)
                    >= self.tracking_collector.min_batch_size
                ):
                    self.tracking_collector.add_batch()
                    self.tracking_collector.reset_batch()

                return True  # close the main menu

            case "[3] Mode":
                mode_choice = None
                while mode_choice == None:
                    mode_choice = action[choice]().chosen_menu_index

                mode_action = self.console.process_mode_menu_choice(mode_choice)
                return self.execute_mode_choice(mode_choice, mode_action)

            case "[4] Config":
                config_menu_exit = False
                while not config_menu_exit:
                    print(config_usage)
                    # ensure valid config menu choice
                    config_choice = None
                    while config_choice == None:
                        config_choice = action[choice]().chosen_menu_index

                    config_action = self.console.process_config_menu_choice(
                        config_choice
                    )
                    config_menu_exit = self.execute_config_choice(
                        config_choice, config_action
                    )

                return False  # keep the main menu open

            case _:
                return action[choice]()

    def execute_mode_choice(self, choice, action):
        """
        Execute the mode choice.
        """
        match console.menus["mental-modes"]["options"][choice]:
            case "[1] normal":
                self.set_mode(action[choice]())
            case "[2] focus":
                self.set_mode(action[choice]())
            case "[3] custom":
                self.set_mode(action[choice]())
            case "[4] back":
                action[choice]()
                return False  # keep the main menu open

        return True  # close the main menu

    def execute_config_choice(self, choice, action):
        """
        Execute the config choice.
        """
        match console.menus["config"]["options"][choice]:
            case "[1] Set batch size":
                input_batch_size = action[choice]
                self.set_batch_size(App.get_float_from_input(input_batch_size))
            case "[2] Set idle limit":
                input_idle_limit = action[choice]
                self.set_idle_limit(App.get_float_from_input(input_idle_limit))
            case "[3] Set dataset size":
                input_dataset_size = action[choice]
                self.set_dataset_size(App.get_float_from_input(input_dataset_size))
            case "[4] Back":
                action[choice]()
                return True  # close the config menu

        return False  # keep the config menu open

    # TODO: Move these into tracking collector
    def set_mode(self, mode):
        """
        Set the mode.
        """
        if mode == "custom":
            self.set_custom_mode()

        else:
            self.tracking_collector.max_dataset_size = modes[mode]["MAX_DATASET_SIZE"]
            self.tracking_collector.max_batch_size = modes[mode]["MAX_BATCH_SIZE"]
            self.timer.idle_limit = modes[mode]["IDLE_LIMIT"]

        mode_info = f"""
{mode} mode
    Dataset size: {self.tracking_collector.max_dataset_size / self.tracking_collector.max_batch_size} batches, {self.tracking_collector.max_dataset_size} samples
    Batch size: {self.tracking_collector.max_batch_size} samples
    Idle limit: {self.timer.idle_limit / 60 / 1e9} minutes
"""

        print(mode_info)

    def set_custom_mode(self):
        """
        Set the custom mode.
        """
        # set the batch size
        while True:
            try:
                max_batch_size = int(input("Enter the max batch size: "))
                if max_batch_size < 100:
                    print("Batch size must contain at least 100 samples.")
                    continue

                self.tracking_collector.max_batch_size = max_batch_size
                break

            except ValueError:
                print("Please enter a number.")
                continue

        # set the idle limit
        while True:
            try:
                idle_limit = float(input("Enter the idle limit: ")) * 60 * 1e9
                if idle_limit < 0.5:
                    print("Idle limit must be at least 30 seconds.")
                    continue

                self.timer.idle_limit = idle_limit
                break

            except ValueError:
                print("Please enter a number.")
                continue

        # set the dataset size
        while True:
            try:
                max_dataset_size = (
                    int(input("Enter the max dataset size: "))
                    * self.tracking_collector.max_batch_size
                )

                if max_dataset_size < 1:
                    print("Dataset size must contain at least one batch.")
                    continue

                self.tracking_collector.max_dataset_size = max_dataset_size
                break

            except ValueError:
                print("Please enter a number.")
                continue

    def set_dataset_size(self, dataset_size):
        """
        Set the dataset size.
        """
        # ensure the dataset size is at least one batch
        if dataset_size < 1:
            print("Dataset size must contain at least one batch.")
            return

        # cast the dataset size to an integer
        self.tracking_collector.max_dataset_size = (
            int(dataset_size) * self.tracking_collector.max_batch_size
        )
        print(
            f"Dataset size set to {self.tracking_collector.max_dataset_size / self.tracking_collector.max_batch_size} batches, {self.tracking_collector.max_dataset_size} samples"
        )

    def set_batch_size(self, batch_size):
        """
        Set the batch size.
        """
        # ensure the batch size is at least 100 samples
        if batch_size < 100:
            print("Batch size must contain at least 100 samples.")
            return

        # cast the batch size to an integer
        self.tracking_collector.max_batch_size = int(batch_size)
        print(f"Batch size set to {self.tracking_collector.max_batch_size} samples")

    def set_idle_limit(self, idle_limit):
        """
        Set the idle limit.
        """
        # ensure the idle limit is at least 30 seconds
        if idle_limit < 0.5:
            print("Idle limit must be at least 30 seconds.")
            return

        self.timer.idle_limit = idle_limit * 60 * 1e9
        print(f"Idle limit set to {self.timer.idle_limit / 60 / 1e9} minutes")

    @staticmethod
    def get_float_from_input(input_action):
        """
        Get a floating point number from the user input.
        """
        while True:
            try:
                return float(input_action())
            except ValueError:
                print("Please enter a number.")
                continue
