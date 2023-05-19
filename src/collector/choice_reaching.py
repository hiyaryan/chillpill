import time

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
field_index = {elem: idx for idx, elem in enumerate(FIELDS)}

# estimated batch of clean data that can be collected before idle timeout
MAX_BATCH_SIZE = 5000

# estimated batch size for sufficient instances to represent a feeling
MIN_BATCH_SIZE = 1000


class ChoiceReaching:
    def __init__(self, dataset=[FIELDS], batch_size=1):
        self.dataset = dataset
        self.batch = []
        self.batch_num = int(len(dataset) / batch_size)
        self.feeling = 2

    def set_feeling(self, feeling):
        """
        Set the feeling for the completed batch.
        """
        self.feeling = feeling
        for row in self.batch:
            row[field_index["feeling"]] = feeling

    def reset_batch(self):
        """
        Reset the working batch.
        """
        self.batch = []

    def reset_dataset(self):
        """
        Reset the dataset and batch number.
        """
        self.dataset = [FIELDS]
        self.batch_num = 1

    def add_batch(self):
        """
        Add the working batch to the dataset and increment batch number.
        """
        self.dataset.extend(self.batch)
        self.batch_num += 1

    def add_row(self, data={}):
        """
        Add a single row of data to the dataset.
        """
        row = [0] * len(FIELDS)

        row[field_index["id"]] = len(self.batch) + len(self.dataset)
        row[field_index["batch"]] = self.batch_num
        row[field_index["time"]] = time.time()

        for field in data.keys():
            row[field_index[field]] = data[field]

        row[field_index["feeling"]] = -1

        print(row)
        self.batch.append(row)
