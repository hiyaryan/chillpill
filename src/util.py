import os
import csv

TRACKING_PATH = os.path.join("data", "tracking")


def get_tracking_path(filename):
    return os.path.join(TRACKING_PATH, filename)


def write_tracking_file(filename, dataset):
    with open(get_tracking_path(filename), "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(dataset)
