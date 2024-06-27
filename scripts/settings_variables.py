import os
import sys
import json

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller stores temporary files in _MEIPASSyyh
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load configuration
config_path = resource_path("config.json")
with open(config_path, "r") as f:
    config = json.load(f)

# Assign settings from config
SENDER_EMAIL = config["SENDER_EMAIL"]
SENDER_PASSWORD = config["SENDER_PASSWORD"]
MY_FRAME_01 = resource_path(config["MY_FRAME_01"])
MY_FRAME_02 = resource_path(config["MY_FRAME_02"])
MY_Frame = resource_path(config["MY_Frame"])
WEBCAM_WIDTH = config["WEBCAM_WIDTH"]
WEBCAM_HEIGHT = config["WEBCAM_HEIGHT"]
MESSAGE_SUBJECT = config["MESSAGE_SUBJECT"]
MESSAGE_BODY = config["MESSAGE_BODY"]
INTRO_VIDEO = resource_path(config["INTRO_VIDEO"])
BACKGROUND_IMAGE = resource_path(config.get("BACKGROUND_IMAGE", "default_background.jpg"))  # New background image setting
