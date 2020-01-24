# -*- coding: utf-8 -*-

import requests
import json
import datetime
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_posts_after(time):
    """
    Get posts from Fiirumi that are created after the given time in UTC.
    """
    url = "https://fiirumi.fyysikkokilta.fi/posts.json"
    res = requests.get(url)
    data = json.loads(res.text)

    posts = [x for x in data["latest_posts"] if x["created_at"] > time]

    return posts

def check_messages(bot, update):

    global keyboard

    lorina_id = 7

    data = load_data()

    posts = get_posts_after(data["previous_messages"])
    data["previous_messages"] = datetime.datetime.utcnow().isoformat()

    for p in posts:
        for c in data["chats"]:
            msg = format_message(p)
            data = load_data()
            if not (p["category_id"] == lorina_id and c["name"] == "Fyysikkokilta"):
                text = format_message(p)
                msg = bot.send_message(c["id"], text, reply_markup=keyboard, parse_mode="MARKDOWN")
                data["sent_messages"].append({"username": p["username"], "chat": msg.chat.id, "message": msg.message_id})


    save_data(data)

def vote_message(bot, update):

    data = load_data()

    message = update.effective_message.message_id
    chat = update.effective_chat.id

    emoji = update.callback_query.data.split(" ")[-1]
    username = [x["username"] for x in data["sent_messages"] if x["chat"] == chat and x["message"] == message][0]

    index = [data.index(x) for x in data["users"] if x["username"] == username][0]
    user = data["users"][index]

    try:
        user["emojis"][emoji] += 1
    except KeyError:
        user["emojis"][emoji] = 1

    data["users"][index] = user

    bot.edit_message_text(
        chat_id = chat,
        message_id = message,
        text = update.effective_message.text,
        reply_markup = InlineKeyboardMarkup(update_keyboard(update.message.reply_markup.inline_keyboard, emoji))
    )

    save_data(data)

def format_message(post):

    data = load_data()
    base_url = "https://fiirumi.fyysikkokilta.fi/t/"

    user = [x for x in data["users"] if x["username"] == post["username"]]

    emojis = None
    if len(user) == 0:
        data["users"] += [{"username": post["username"], "emojis": {}}]
        print(data["users"])
        emojis = {}
    else:
        emojis = user[0]["emojis"]

    emoji_string = " " +  "".join([str(emojis[key]) for key in emojis])

    text = "Uusi postaus Φiirumilla!\n\n *{}*\n _{}_({}{}) \n\n [Lue koko postaus]({})"
    text = text.format(post["topic_title"], post["name"], post["username"],
                       emoji_string, base_url + post["topic_slug"])

    save_data(data)
    return text

def update_keyboard(keyboard, emoji):

    idx = [keyboard[0].index(e) for e in keyboard[0] if e.callback_data == emoji][0]
    text = keyboard[0][idx].text.split(" ")
    if len(text) == 2:
        number = str(int(text[0]) + 1)
    else:
        number = 1

    keyboard[0][idx].text = "{} {}".format(number, emoji)

    return keyboard

def subscribe(bot, update):

    data = load_data()
    data["chats"].append({"name": update.effective_chat.title, "id": update.effective_chat.id})
    save_data(data)
    bot.send_message(update.effective_chat.id, "Fiirumipäivitykset tilattu onnistuneesti")


def load_data():
    global data_file
    with open(data_file) as d:
        data = json.loads(d.read())

    return data

def save_data(data):
    global data_file
    with open(data_file, "w") as d:
        d.write(json.dumps(data))

def create_data():

    data = {}

    data["users"] = []
    data["chats"] = []
    data["sent_messages"] = []
    data["previous_messages"] = datetime.datetime.utcnow().isoformat()

    save_data(data)

data_file = "fiirumi_data.json"

if not os.path.isfile(data_file):
    create_data()

emojis = ["👍","😂","😍","🎉","🙈","💩"]
keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(i, callback_data=i) for i in emojis]])
