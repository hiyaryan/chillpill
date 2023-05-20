import simple_term_menu as stm

from util.constants import MENUS


class ConsoleMenu:
    def __init__(self, title="", options=[]):
        self.title = title
        self.options = options

    def run(self):
        terminal_menu = stm.TerminalMenu(self.options, title=self.title)
        terminal_menu.show()
        return terminal_menu

    def get_terminal_menu(self, menu_name):
        menu = MENUS[menu_name]
        self.title = menu["title"]
        self.options = menu["options"]

        return self

    def process_main_menu_choice(self, app, choice):
        """
        Takes the index from the main menu and return an action to be performed.
        """
        match MENUS["main-menu"]["options"][choice]:
            case "[1] Resume":
                return {choice: lambda: True}
            case "[2] Check-in":
                return {choice: lambda: self.get_terminal_menu("check-in").run()}
            case "[3] Mode":
                return {choice: lambda: self.get_terminal_menu("mental-modes").run()}
            case "[4] Config":
                return {choice: lambda: self.get_terminal_menu("config").run()}
            case "[5] Quit":
                return {choice: lambda: app.quit()}

    def process_mode_menu_choice(self, choice):
        """
        Takes the index from the mode menu and return an action to be performed.
        """
        match MENUS["mental-modes"]["options"][choice]:
            case "[1] normal":
                return {choice: lambda: "normal"}
            case "[2] focus":
                return {choice: lambda: "focus"}
            case "[3] custom":
                return {choice: lambda: "custom"}
            case "[4] back":
                return {choice: lambda: ()}

    def process_config_menu_choice(self, choice):
        """
        Takes the index from the config menu and return an action to be performed.
        """
        match MENUS["config"]["options"][choice]:
            case "[1] Set batch size":
                return {choice: lambda: input("Enter batch size: ")}
            case "[2] Set idle limit":
                return {choice: lambda: input("Enter idle limit: ")}
            case "[3] Set dataset size":
                return {choice: lambda: input("Enter dataset size: ")}
            case "[4] Back":
                return {choice: lambda: ()}
