"""
This package looks Discourse api for new posts and replies in
https://fiirumi.fyysikkokilta.fi and notifies about them in chats where
notifications are subscribed and also provides emoji responses for new posts.
"""

import requests
import json
import datetime
import os

from telegram.error import BadRequest
from telegram import Update
from ..utils import CallbackContext

import config


FIIRUMI_DATA_FILE = "data/fiirumi_data.json"


def get_posts_after(time):
    """
    Get posts from Fiirumi that are created after the given time in UTC.
    """
    res = requests.get(config.FIIRUMI_BASE_URL + "/posts.json")
    data = json.loads(res.text)

    posts = [x for x in data["latest_posts"] if x["created_at"] > time]

    posts.reverse()

    return posts


async def check_messages(context: CallbackContext):
    global keyboard
    global data
    lorina_id = 7
    data = load_data()
    posts = get_posts_after(data["previous_messages"])
    data["previous_messages"] = datetime.datetime.utcnow().isoformat()
    try:
        for p in posts:
            for c in data["chats"]:
                msg = format_message(p)
                if not (p["category_id"] == lorina_id and c["name"] == "Fyysikkokilta"):
                    text = format_message(p)
                    print("{} {}".format(c["id"], c["name"]))
                    try:
                        msg = await context.bot.send_message(c["id"], text, parse_mode="MARKDOWN")
                        data["sent_messages"].append(
                            {
                                "username": p["username"],
                                "chat": msg.chat.id,
                                "message": msg.message_id,
                                "voters": {},
                            }
                        )
                    except BadRequest:
                        print("Sending message {} to {} failed.".format(text, c["name"]))
    finally:
        save_data(data)


def format_message(post):
    global data

    user = [x for x in data["users"] if x["username"] == post["username"]]

    if len(user) == 0:
        data["users"] += [{"username": post["username"], "emojis": {}}]

    post_type = "vastaus" if post["post_number"] > 1 else "postaus"

    text = "Uusi {} Φrumilla!\n\n *{}*\n _{}_ ({}) \n\n[Lue koko postaus]({})"
    text = text.format(
        post_type,
        post["topic_title"],
        post["name"],
        post["username"].replace("_", "\\_"),
        config.FIIRUMI_BASE_URL + "/t/" + post["topic_slug"],
    )

    return text


async def subscribe(update: Update, context: CallbackContext):
    assert update.effective_chat is not None, "Update unexpectedly initiated outside of chat"
    global data
    data = load_data()
    chats = [x["id"] for x in data["chats"]]
    if update.effective_chat.id not in chats:
        data["chats"].append({"name": update.effective_chat.title, "id": update.effective_chat.id})
        save_data(data)
        await context.bot.send_message(update.effective_chat.id, "Fiirumipäivitykset tilattu onnistuneesti")
    else:
        await context.bot.send_message(update.effective_chat.id, "Fiirumipäivitykset on jo tilattu")


def load_data():
    with open(FIIRUMI_DATA_FILE) as d:
        data = json.loads(d.read())

    return data


def save_data(data):
    with open(FIIRUMI_DATA_FILE, "w") as d:
        json.dump(data, d, indent=2)


def create_data():
    data = {}

    data["users"] = []
    data["chats"] = []
    data["sent_messages"] = []
    data["previous_messages"] = datetime.datetime.utcnow().isoformat()

    save_data(data)


if not os.path.isfile(FIIRUMI_DATA_FILE):
    create_data()

global data
data = load_data()
