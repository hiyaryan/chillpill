import datetime
import os

import util.file as file_util

from collectors.tracking import TrackingCollector

from listeners.mouse import MouseListener
from listeners.keyboard import KeyboardListener

from gui import chat

from util.console import ConsoleMenu
from util.constants import USAGE, GLOBAL_HOTKEYS, MENUS, CONFIG_USAGE


class App:
    def __init__(self):
        print(USAGE)

        # user name set on chat launch
        self.user_name = None

        # initialize the collector
        # if a saved shot exists, load it
        if os.path.exists(file_util.get_saved_shot_path("wip.json")):
            print("`wip.json` file found. Resuming progress...")

            # load the WIP file
            saved_shot = file_util.load_saved_shot_file("wip.json")

            # initialize the collector with the contents of the WIP file
            self.tracking_collector = TrackingCollector(
                dataset=saved_shot["dataset"],
                config=saved_shot["config"],
            )

        # otherwise, initialize the collector with a new dataset
        else:
            print("No `wip.json` file found. Initializing new dataset...\n")
            self.tracking_collector = TrackingCollector()

        # initialize the listeners for mouse and keyboard
        self.mouse_listener = MouseListener(
            self.tracking_collector, self.tracking_collector.timer
        )

        self.keyboard_listener = KeyboardListener(
            self.tracking_collector, self.tracking_collector.timer
        )

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
                if self.keyboard_listener.hotkey in GLOBAL_HOTKEYS:
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
                    self.tracking_collector.timer.greater_than_idle_limit()
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
            file_util.write_saved_shot_file(
                self.tracking_collector,
                datetime.datetime.now().strftime("wip" + ".json"),
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
        if GLOBAL_HOTKEYS[self.keyboard_listener.hotkey] == "main-menu":
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

        elif GLOBAL_HOTKEYS[self.keyboard_listener.hotkey] == "help":
            print(USAGE)

        elif GLOBAL_HOTKEYS[self.keyboard_listener.hotkey] == "quit":
            self.quit()

        elif GLOBAL_HOTKEYS[self.keyboard_listener.hotkey] == "chat":
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
        match MENUS["main-menu"]["options"][choice]:
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
                    print(CONFIG_USAGE)
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
        match MENUS["mental-modes"]["options"][choice]:
            case "[1] normal":
                self.tracking_collector.set_mode(action[choice]())
            case "[2] focus":
                self.tracking_collector.set_mode(action[choice]())
            case "[3] custom":
                self.tracking_collector.set_mode(action[choice]())
            case "[4] back":
                action[choice]()
                return False  # keep the main menu open

        return True  # close the main menu

    def execute_config_choice(self, choice, action):
        """
        Execute the config choice.
        """
        match MENUS["config"]["options"][choice]:
            case "[1] Set batch size":
                input_batch_size = action[choice]
                self.tracking_collector.set_batch_size(
                    App.get_float_from_input(input_batch_size)
                )
            case "[2] Set idle limit":
                input_idle_limit = action[choice]
                self.tracking_collector.set_idle_limit(
                    App.get_float_from_input(input_idle_limit)
                )
            case "[3] Set dataset size":
                input_dataset_size = action[choice]
                self.tracking_collector.set_dataset_size(
                    App.get_float_from_input(input_dataset_size)
                )
            case "[4] Back":
                action[choice]()
                return True  # close the config menu

        return False  # keep the config menu open

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
