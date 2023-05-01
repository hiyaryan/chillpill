import time

FIELDS = ["id", "time", "x", "y", "scroll", "press", "release"]
field_index = {elem: idx for idx, elem in enumerate(FIELDS)}


class ChoiceReaching:
    def __init__(self):
        self.dataset = [FIELDS]

    def reset(self):
        """
        Reset the dataset.
        """
        self.dataset = [FIELDS]

    def add_row(self, data={}):
        """
        Add a single row of data to the dataset.
        """
        row = [0] * len(FIELDS)

        row[field_index["id"]] = len(self.dataset)
        row[field_index["time"]] = time.time()

        for field in data.keys():
            row[field_index[field]] = data[field]

        self.dataset.append(row)
