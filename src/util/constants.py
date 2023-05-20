# the maximum number of samples to collect before writing to a file
MAX_DATASET_SIZE = 1e5

# estimated batch of clean data that can be collected before idle timeout
MAX_BATCH_SIZE = 5000

# estimated batch size for sufficient instances to represent a feeling
MIN_BATCH_SIZE = 1000

# 5 minutes in nanoseconds
IDLE_LIMIT = 5 * 60 * 1e9

# dataset fields
FIELDS = [
    "id",
    "batch",
    "time",
    "input_type",
    "x",
    "y",
    "scroll",
    "press",
    "release",
    "feeling",
]

# dictionary of global hotkeys and their actions
GLOBAL_HOTKEYS = {
    "<ctrl>+<q>": "quit",
    "<ctrl>+<m>": "main-menu",
    "<ctrl>+<h>": "help",
    "<ctrl>+<o>": "chat",
}

# list of hotkeys and menus
USAGE = """
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

# description of configurable parameters
CONFIG_USAGE = """
Configurations:
    batch size: set the number of tracking instances per trial
    idle limit: set the allowable idle minutes before a trial is reset
    dataset size: set the number of trials per dataset
"""

# dictionary of menus and their options
MENUS = {
    "main-menu": {
        "title": "Main Menu",
        "options": [
            "[1] Resume",
            "[2] Check-in",
            "[3] Mode",
            "[4] Config",
            "[5] Quit",
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
            "[3] custom",
            "[4] back",
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
