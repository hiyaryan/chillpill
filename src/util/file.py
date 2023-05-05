import os
import csv
import json

TRACKING_PATH = os.path.join("data", "tracking")

# the maximum number of samples to collect before writing to a file
MAX_DATASET_SIZE = 1e5

# path for data saved on program quit
SAVED_SHOT_PATH = os.path.join("data", "saved")

#
SAVED_SHOT_TEMPLATE = {
    "config": {},
    "dataset": [],
}


def get_tracking_path(filename):
    return os.path.join(TRACKING_PATH, filename)


def write_tracking_file(filename, dataset):
    with open(get_tracking_path(filename), "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(dataset)


def get_saved_shot_path(filename):
    return os.path.join(SAVED_SHOT_PATH, filename)


def write_saved_shot_file(filename, template):
    with open(get_saved_shot_path(filename), "w") as jsonfile:
        json.dump(template, jsonfile)


def load_saved_shot_file(filename):
    with open(get_saved_shot_path(filename), "r") as jsonfile:
        return json.load(jsonfile)
