import time

from util.timer import Timer
from util.templates import MODES
from util.constants import (
    FIELDS,
    IDLE_LIMIT,
    MAX_DATASET_SIZE,
    MAX_BATCH_SIZE,
    MIN_BATCH_SIZE,
)


class TrackingCollector:
    def __init__(self, dataset=None, config=None):
        self.field_index = {elem: idx for idx, elem in enumerate(FIELDS)}

        self.dataset = dataset if dataset else [FIELDS]

        self.batch = []
        self.batch_size = config["batch_size"] if config else 1
        self.batch_num = int(len(self.dataset) / self.batch_size)

        self.idle_limit = config["idle_limit"] if config else IDLE_LIMIT
        self.timer = Timer(self.idle_limit)

        self.feeling = 2

        self.max_dataset_size = config["dataset_size"] if config else MAX_DATASET_SIZE
        self.max_batch_size = config["batch_size"] if config else MAX_BATCH_SIZE
        self.min_batch_size = MIN_BATCH_SIZE

        if config:
            self.print_config()

    def add_row(self, data={}):
        """
        Add a single row of data to the dataset.
        """
        row = [0] * len(FIELDS)

        row[self.field_index["id"]] = len(self.batch) + len(self.dataset)
        row[self.field_index["batch"]] = self.batch_num
        row[self.field_index["time"]] = time.time()

        for field in data.keys():
            row[self.field_index[field]] = data[field]

        row[self.field_index["feeling"]] = -1

        print(row)
        self.batch.append(row)

    def set_feeling(self, feeling):
        """
        Set the feeling for the completed batch.
        """
        self.feeling = feeling
        for row in self.batch:
            row[self.field_index["feeling"]] = feeling

    def set_dataset_size(self, dataset_size):
        """
        Set the dataset size.
        """
        # ensure the dataset size is at least one batch
        if dataset_size < 1:
            print("Dataset size must contain at least one batch.")
            return False

        # cast the dataset size to an integer
        self.max_dataset_size = int(dataset_size) * self.max_batch_size
        print(
            f"Dataset size set to {self.max_dataset_size / self.max_batch_size} batches, {self.max_dataset_size} samples"
        )

        return True

    def reset_dataset(self):
        """
        Reset the dataset and batch number.
        """
        self.dataset = [FIELDS]
        self.batch_num = 1

    def set_batch_size(self, batch_size):
        """
        Set the batch size.
        """
        # ensure the batch size is at least 100 samples
        if batch_size < 100:
            print("Batch size must contain at least 100 samples.")
            return False

        # cast the batch size to an integer
        self.max_batch_size = int(batch_size)
        print(f"Batch size set to {self.max_batch_size} samples")

        return True

    def add_batch(self):
        """
        Add the working batch to the dataset and increment batch number.
        """
        self.dataset.extend(self.batch)
        self.batch_num += 1

    def reset_batch(self):
        """
        Reset the working batch.
        """
        self.batch = []

    def set_idle_limit(self, idle_limit):
        """
        Set the idle limit.
        """
        # ensure the idle limit is at least 30 seconds
        if idle_limit < 0.5:
            print("Idle limit must be at least 30 seconds.")
            return False

        self.timer.idle_limit = idle_limit * 60 * 1e9
        print(f"Idle limit set to {self.timer.idle_limit / 60 / 1e9} minutes")

        return True

    def set_mode(self, mode):
        """
        Set the mode.
        """
        if mode == "custom":
            self.set_custom_mode()

        else:
            self.max_dataset_size = MODES[mode]["MAX_DATASET_SIZE"]
            self.max_batch_size = MODES[mode]["MAX_BATCH_SIZE"]
            self.timer.idle_limit = MODES[mode]["IDLE_LIMIT"]

        self.print_config(mode)

    def set_custom_mode(self):
        """
        Set the custom mode.
        """
        # set the batch size
        while True:
            try:
                max_batch_size = int(input("Enter the max batch size: "))
                if not self.set_batch_size(max_batch_size):
                    continue

                break

            except ValueError:
                print("Please enter a number.")
                continue

        # set the idle limit
        while True:
            try:
                idle_limit = float(input("Enter the idle limit: "))
                if not self.set_idle_limit(idle_limit):
                    continue

                break

            except ValueError:
                print("Please enter a number.")
                continue

        # set the dataset size
        while True:
            try:
                max_dataset_size = (
                    int(input("Enter the max dataset size: ")) * self.max_batch_size
                )

                if not self.set_dataset_size(max_dataset_size):
                    continue

                break

            except ValueError:
                print("Please enter a number.")
                continue

    def print_config(self, mode=""):
        """
        Print the current configuration.
        """

        title = "Configuration" if not mode else f"{mode.capitalize()} Mode"

        configuration = f"""
{title}:
    Dataset size: {self.max_dataset_size / self.max_batch_size} batches, {self.max_dataset_size} samples
    Batch size: {self.max_batch_size} samples
    Idle limit: {self.timer.idle_limit / 60 / 1e9} minutes\n"""

        print(configuration)
