from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener

import listeners.keyboard as virtual_keyboard

import collector.choice_reaching as choice_reaching
from collector.choice_reaching import ChoiceReaching

import util.file as file
import util.console as console
import util.timer as timer

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

# TODO: add the mental modes, this will be built-in default configurations, note the custom option will prompt the user with the config menu and will save the new custom mode to a config.json file. This is the only method that will save a new mode, if the user makes changes in config mode, then the configuration will only be saved in runtime memory.
modes = {
    "normal": {
        "MAX_BATCH_SIZE": 2500,
        "IDLE_LIMIT": 5 * 60 * 1e9,
        "MAX_DATASET_SIZE": 5e4,
    },
    "focus": {
        "MAX_BATCH_SIZE": 5000,
        "IDLE_LIMIT": 10 * 60 * 1e9,
        "MAX_DATASET_SIZE": 1e5,
    },
    "custom": {
        "MAX_BATCH_SIZE": 0,
        "IDLE_LIMIT": 0,
        "MAX_DATASET_SIZE": 0,
    },
}


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
                    and len(self.choice_reaching_collector.batch)
                    % choice_reaching.MAX_BATCH_SIZE
                    == 0
                ):
                    self.feeling_selected = True
                    self.toggle_listening()
                    self.activate_window()  # bring the terminal to the front

                    # open the check-in menu and set the current feeling
                    check_in_choice = self.get_choice_from_menu("check-in")
                    self.choice_reaching_collector.set_feeling(check_in_choice)
                    self.choice_reaching_collector.add_batch()
                    self.choice_reaching_collector.reset_batch()

                    print(
                        f"Dataset length {len(self.choice_reaching_collector.dataset)}/{file.MAX_DATASET_SIZE}"
                    )
                    self.toggle_listening()

                # reset the feeling selected flag
                elif (
                    self.feeling_selected
                    and len(self.choice_reaching_collector.batch)
                    % choice_reaching.MAX_BATCH_SIZE
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

    def quit(self):
        # TODO: Should save progress on working dataset. If less than 100000 save to WIP file. On startup load the dataset from the WIP file and continue. Use pickle to save the dataset as a dictionary instead of a CSV.
        self.stop_listeners()
        exit()

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

                self.choice_reaching_collector.set_feeling(check_in_choice)
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
                self.set_batch_size(self.get_float_from_input(input_batch_size))
            case "[2] Set idle limit":
                input_idle_limit = action[choice]
                self.set_idle_limit(self.get_float_from_input(input_idle_limit))
            case "[3] Set dataset size":
                input_dataset_size = action[choice]
                self.set_dataset_size(self.get_float_from_input(input_dataset_size))
            case "[4] Back":
                action[choice]()
                return True  # close the config menu

        return False  # keep the config menu open

    # TODO: Move static methods to a separate utility file
    @staticmethod
    def set_mode(mode):
        """
        Set the mode.
        """
        if mode == "custom":
            Application.set_custom_mode()

        else:
            choice_reaching.MAX_BATCH_SIZE = modes[mode]["MAX_BATCH_SIZE"]
            timer.IDLE_LIMIT = modes[mode]["IDLE_LIMIT"]
            file.MAX_DATASET_SIZE = modes[mode]["MAX_DATASET_SIZE"]

        mode_info = f"""
{mode} mode
    Batch size: {choice_reaching.MAX_BATCH_SIZE} samples
    Idle limit: {timer.IDLE_LIMIT / 60 / 1e9} minutes
    Dataset size: {file.MAX_DATASET_SIZE / choice_reaching.MAX_BATCH_SIZE} batches, {file.MAX_DATASET_SIZE} samples
"""

        print(mode_info)

    @staticmethod
    def set_custom_mode():
        """
        Set the custom mode.
        """
        # set the batch size
        while True:
            try:
                choice_reaching.MAX_BATCH_SIZE = int(
                    input("Enter the max batch size: ")
                )
                if choice_reaching.MAX_BATCH_SIZE < 100:
                    print("Batch size must contain at least 100 samples.")
                    continue
                break
            except ValueError:
                print("Please enter a number.")
                continue

        # set the idle limit
        while True:
            try:
                timer.IDLE_LIMIT = float(input("Enter the idle limit: ")) * 60 * 1e9
                if timer.IDLE_LIMIT < 0.5:
                    print("Idle limit must be at least 30 seconds.")
                    continue
                break
            except ValueError:
                print("Please enter a number.")
                continue

        # set the dataset size
        while True:
            try:
                file.MAX_DATASET_SIZE = (
                    int(input("Enter the max dataset size: "))
                    * choice_reaching.MAX_BATCH_SIZE
                )

                if file.MAX_DATASET_SIZE < 1:
                    print("Dataset size must contain at least one batch.")
                    continue
                break
            except ValueError:
                print("Please enter a number.")
                continue

    @staticmethod
    def set_batch_size(batch_size):
        """
        Set the batch size.
        """
        # ensure the batch size is at least 100 samples
        if batch_size < 100:
            print("Batch size must contain at least 100 samples.")
            return

        # cast the batch size to an integer
        choice_reaching.MAX_BATCH_SIZE = int(batch_size)
        print(f"Batch size set to {choice_reaching.MAX_BATCH_SIZE} samples")

    @staticmethod
    def set_idle_limit(idle_limit):
        """
        Set the idle limit.
        """
        # ensure the idle limit is at least 30 seconds
        if idle_limit < 0.5:
            print("Idle limit must be at least 30 seconds.")
            return

        timer.IDLE_LIMIT = idle_limit * 60 * 1e9
        print(f"Idle limit set to {timer.IDLE_LIMIT / 60 / 1e9} minutes")

    @staticmethod
    def set_dataset_size(dataset_size):
        """
        Set the dataset size.
        """
        # ensure the dataset size is at least one batch
        if dataset_size < 1:
            print("Dataset size must contain at least one batch.")
            return

        # cast the dataset size to an integer
        file.MAX_DATASET_SIZE = int(dataset_size) * choice_reaching.MAX_BATCH_SIZE
        print(
            f"Dataset size set to {file.MAX_DATASET_SIZE / choice_reaching.MAX_BATCH_SIZE} batches, {file.MAX_DATASET_SIZE} samples"
        )

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
