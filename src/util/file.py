import os
import csv
import json
import pandas as pd

TRACKING_PATH = os.path.join("data", "tracking")

# the maximum number of samples to collect before writing to a file
MAX_DATASET_SIZE = 1e5

# preprocessed data path
PREPROCESSED_PATH = os.path.join("data", "preprocessed")

# preprocessed paths to individual input types
MOUSE_MOTION_TRACKING_PATH = os.path.join(PREPROCESSED_PATH, "mouse_motion")
MOUSE_CLICK_TRACKING_PATH = os.path.join(PREPROCESSED_PATH, "mouse_click")
KEYBOARD_INPUT_TRACKING_PATH = os.path.join(PREPROCESSED_PATH, "keyboard_input")
SCROLLING_TRACKING_PATH = os.path.join(PREPROCESSED_PATH, "scrolling")

# path for data saved on program quit
SAVED_SHOT_PATH = os.path.join("data", "saved")

SAVED_SHOT_TEMPLATE = {
    "config": {},
    "dataset": [],
}


def get_tracking_path(filename):
    tracking_path = os.path.join(TRACKING_PATH, filename)
    if not os.path.exists(os.path.dirname(tracking_path)):
        os.makedirs(os.path.dirname(tracking_path))
    return os.path.join(TRACKING_PATH, filename)


def write_tracking_file(filename, dataset):
    with open(get_tracking_path(filename), "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(dataset)


def load_tracking_file(filename):
    """
    Returns a pandas dataframe of the tracking data.
    """
    return pd.read_csv(get_tracking_path(filename))


def get_preprocessed_path(filename):
    preprocessed_path = os.path.join(PREPROCESSED_PATH, filename)
    if not os.path.exists(os.path.dirname(preprocessed_path)):
        os.makedirs(os.path.dirname(preprocessed_path))
    return preprocessed_path


def write_preprocessed_file_from_dataframe(filename, dataframe):
    dataframe.to_csv(get_preprocessed_path(filename), index=False)


def load_preprocessed_file(filename):
    """
    Returns a pandas dataframe of the preprocessed data.
    """
    return pd.read_csv(get_preprocessed_path(filename))


def get_input_type_path(input_type, filename):
    """
    Gets the path to the preprocessed file for the given input type.
    """

    if input_type == "mouse_motion" or input_type == 1:
        input_type_path = os.path.join(MOUSE_MOTION_TRACKING_PATH, filename)
    elif input_type == "mouse_click" or input_type == 2:
        input_type_path = os.path.join(MOUSE_CLICK_TRACKING_PATH, filename)
    elif input_type == "keyboard_input" or input_type == 3:
        input_type_path = os.path.join(KEYBOARD_INPUT_TRACKING_PATH, filename)
    elif input_type == "scrolling" or input_type == 4:
        input_type_path = os.path.join(SCROLLING_TRACKING_PATH, filename)
    else:
        raise ValueError("Invalid input type: {}".format(input_type))

    if not os.path.exists(os.path.dirname(input_type_path)):
        os.makedirs(os.path.dirname(input_type_path))
    return input_type_path


def write_preprocessed_file_by_input_type_from_dataframe(
    input_type, filename, dataframe
):
    dataframe.to_csv(get_input_type_path(input_type, filename), index=False)


def load_preprocessed_file_by_input_type(input_type, filename):
    """
    Returns a pandas dataframe of the preprocessed data for the given input type.
    """
    return pd.read_csv(get_input_type_path(input_type, filename))


def get_saved_shot_path(filename):
    saved_shot_path = os.path.join(SAVED_SHOT_PATH, filename)
    if not os.path.exists(os.path.dirname(saved_shot_path)):
        os.makedirs(os.path.dirname(saved_shot_path))
    return saved_shot_path


def write_saved_shot_file(filename, template):
    with open(get_saved_shot_path(filename), "w") as jsonfile:
        json.dump(template, jsonfile)


def load_saved_shot_file(filename):
    with open(get_saved_shot_path(filename), "r") as jsonfile:
        return json.load(jsonfile)
