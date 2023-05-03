import simple_term_menu as stm


class ConsoleMenu:
    def __init__(self, title, options):
        self.title = title
        self.options = options

    def run(self):
        terminal_menu = stm.TerminalMenu(self.options, title=self.title)
        terminal_menu.show()
        return terminal_menu
