"""
Used to initialize variables such as bot tokens and settings so that they can be used across all the project files.
"""

import json
import db
import sqlite3

from os.path import isfile


def init_settings():

    with open("config.json") as f:
        config = json.load(f)

    global settings
    settings = config["SETTINGS"]

def init_secrets(env):

    import drive

    assert env in ["TEST", "PROD"], "The environment can be either TEST or PROD"

    with open("config.json") as f:
        config = json.load(f)

    global secrets
    global settings

    secrets = drive.get_secrets(env)
    secrets["database"] = "kiltis_{}.db".format(env)
    settings = config["SETTINGS"]

    # assert settings["messaging"] and secrets["chat_id"], \
    # """You must specify a chat id for the chat where the messages will be forwarded
    # if you want to use the messaging feature."""

    # assert not (settings["drive_backend"] and not secrets["tuotteet_sheet"]),\
    # """Must have tuotteet sheet defined if you want to use Drive backend"""

    # assert not (settings["drive_backend"] and not secrets["kayttajat_sheet"]),\
    # """Must have kayttajat sheet defined if you want to use Drive backend"""

    # assert not (settings["drive_backend"] and not secrets["tapahtumat_sheet"]),\
    # """Must have tapahtumat sheet defined if you want to use Drive backend"""

    # assert not ((settings["calendar"] or settings["drive_backend"]) and not isfile("credentials.json")),\
    # """You need the credentials file in this directory from 
    # https://developers.google.com/sheets/api/quickstart/python
    # to use the Google API features.
    # """

    if settings["store"] and (not secrets["database"] or not isfile(secrets["database"])):
        database = "kiltis_{}.db".format(env)
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
        
        



