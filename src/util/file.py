import os
import csv

TRACKING_PATH = os.path.join("data", "tracking")

# the maximum number of samples to collect before writing to a file
MAX_DATASET_SIZE = 1e5


def get_tracking_path(filename):
    return os.path.join(TRACKING_PATH, filename)


def write_tracking_file(filename, dataset):
    with open(get_tracking_path(filename), "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(dataset)
