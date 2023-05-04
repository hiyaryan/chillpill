import simple_term_menu as stm

menus = {
    "main-menu": {
        "title": "Main Menu",
        "options": [
            "[1] Resume",
            "[2] Check-in",
            "[3] Mode",
            "[4] Config",
        ],
    },
    "check-in": {
        "title": "How are you feeling?",
        "options": [
            "[1] bad",
            "[2] okay",
            "[3] neutral",
            "[4] good",
            "[5] great",
        ],
    },
    "mental-modes": {
        "title": "Select a Mode",
        "options": [
            "[1] normal",
            "[2] focus",
            "[3] back",
        ],
    },
    "config": {
        "title": "Config Menu",
        "options": [
            "[1] Set batch size",
            "[2] Set idle limit",
            "[3] Set dataset size",
            "[4] Back",
        ],
    },
}


class ConsoleMenu:
    def __init__(self, title="", options=[]):
        self.title = title
        self.options = options

    def run(self):
        terminal_menu = stm.TerminalMenu(self.options, title=self.title)
        terminal_menu.show()
        return terminal_menu

    def open_menu(self, menu_name):
        menu = menus[menu_name]
        self.title = menu["title"]
        self.options = menu["options"]

        choice = None
        while choice == None:
            choice = self.run().chosen_menu_index

        return choice

    def process_main_menu_choice(self, app, choice):
        match menus["main-menu"]["options"][choice]:
            case "[1] Resume":
                return
            case "[2] Check-in":
                print("check-in")
            case "[3] Mode":
                print("mode")
            case "[4] Config":
                print("config")
