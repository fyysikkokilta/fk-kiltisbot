"""
Initialises variables for the bot
"""

import json
import db
import sqlite3

from os.path import isfile


def init(env):

    assert env in ["TEST", "PROD"], "The environment can be either TEST or PROD"

    with open("config.json") as f:
        config = json.load(f)

    global secrets
    global settings

    secrets = config[env]
    settings = config["SETTINGS"]

    assert settings["messaging"] and secrets["chat_id"], \
    """You must specify a chat id for the chat where the messages will be forwarded
    if you want to use the messging feature."""

    assert not settings["drive_backend"] or (secrets["tuotteet_sheet"] 
    and secrets["kayttajat_sheet"] and secrets["tapahtumat_sheet"]), \
    """You must specify the Google drive sheets used for the backend if 
    you want to use that feature
    """

    assert (settings["calendar"] or settings["drive_backend"]) and isfile("credentials.json")
    """You need the credentials file in this directory from 
    https://developers.google.com/sheets/api/quickstart/python
    to use the Google API features.
    """

    if not secrets["database"] or not isfile(secrets["database"]):
        database = "{}_default.db".format(env)
        print("No such database file as {}. Creating new database {}".format(secrets["database"], database))
        secrets["database"] = database

        config[env]["database"] = database

        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("CREATE TABLE inventory (nimi text, hinta int, maara int)")
        c.execute("CREATE TABLE users (id int, nick text, nimi text, saldo int)")
        c.execute("CREATE TABLE transactions (id integer primary key, user int, user_name text, tuote text, hinta int, aika text)")
        conn.commit()
        conn.close()

        with open("config.json", "w+") as f:
            json.dump(config, f, indent = "\t")
        
        



