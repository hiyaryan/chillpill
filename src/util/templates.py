# template for modes
MODES = {
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

# template for WIP file
SAVED_SHOT = {
    "config": {},
    "dataset": [],
}
