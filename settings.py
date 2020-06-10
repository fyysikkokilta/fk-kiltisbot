"""
Used to initialize variables such as bot tokens and settings so that they can be used across all the project files.
"""

import json
import sqlite3

from os.path import isfile


def init_secrets(env):

    import db.drive

    assert env in ["TEST", "PROD"], "The environment can be either TEST or PROD"

    with open("config.json") as f:
        config = json.load(f)

    global secrets
    global settings

    settings = config["SETTINGS"]
    secrets = db.drive.get_secrets(env)
    secrets["database"] = "kiltis_{}.db".format(env)
