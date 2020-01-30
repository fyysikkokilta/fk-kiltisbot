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
    global data

    lorina_id = 7

    data = load_data()

    posts = get_posts_after(data["previous_messages"])
    data["previous_messages"] = datetime.datetime.utcnow().isoformat()

    for p in posts:
        for c in data["chats"]:
            msg = format_message(p)
            if not (p["category_id"] == lorina_id and c["name"] == "Fyysikkokilta"):
                text = format_message(p)
                msg = bot.send_message(c["id"], text, reply_markup=keyboard, parse_mode="MARKDOWN")
                data["sent_messages"].append({"username": p["username"], "chat": msg.chat.id, "message": msg.message_id, "voters": {}})


    save_data(data)

def vote_message(bot, update):

    global data
    data = load_data()

    message = update.effective_message.message_id
    chat = update.effective_chat.id
    sender = update.effective_user.id
#    #print(update.effective_message.entities)

    emoji = update.callback_query.data.split(" ")[-1]
    index = [data["sent_messages"].index(x) for x in data["sent_messages"] if x["chat"] == chat and x["message"] == message][0]
    sent_message = data["sent_messages"][index]

    #print(sent_message["voters"].keys())
    #print(sender)
    #print(sender in sent_message["voters"].keys())
    if not str(sender) in sent_message["voters"].keys():
        sent_message["voters"][str(sender)] = emoji
        bot.edit_message_reply_markup(
            chat_id = chat,
            message_id = message,
            #text = update.effective_message.text,
            reply_markup = InlineKeyboardMarkup(update_keyboard(update.effective_message.reply_markup.inline_keyboard, emoji, 1)))

        data["sent_messages"][index] = sent_message
        save_data(data)
    else:
        prev_emoji = sent_message["voters"][str(sender)]
        #print(prev_emoji)
        new_keyboard = update_keyboard(update.effective_message.reply_markup.inline_keyboard, prev_emoji, -1)
        #print(new_keyboard)
        new_keyboard =  update_keyboard(new_keyboard, emoji, 1)
        #print(new_keyboard)

        bot.edit_message_reply_markup(
            chat_id = chat,
            message_id = message,
            #text = update.effective_message.text,
            reply_markup = InlineKeyboardMarkup(new_keyboard))

        sent_message["voters"][str(sender)] = emoji

        data["sent_messages"][index] = sent_message
        save_data(data)
    return

def format_message(post):

    global data

    base_url = "https://fiirumi.fyysikkokilta.fi/t/"

    user = [x for x in data["users"] if x["username"] == post["username"]]

    emojis = None
    if len(user) == 0:
        data["users"] += [{"username": post["username"], "emojis": {}}]
        #print(data["users"])
        emojis = {}
    else:
        emojis = user[0]["emojis"]

    emoji_string = " " +  "".join([str(emojis[key]) + key for key in emojis])
    post_type = "vastaus" if post["post_number"] > 1 else "postaus"

    text = "Uusi {} Φrumilla!\n\n *{}*\n _{}_ ({}) \n\n[Lue koko postaus]({})"
    text = text.format(post_type, post["topic_title"], post["name"], post["username"],  base_url + post["topic_slug"])

    return text

def update_keyboard(keyboard, emoji, diff):

    global emojis
    idx = [emojis.index(e) for e in emojis if e == emoji][0]

    #print(idx)
    text = keyboard[0][idx].text.split(" ")
    if len(text) == 2:
        number = str(int(text[0]) + diff)
    else:
        number = 1

    if number == "0":
        keyboard[0][idx].text = emoji
    else:
        keyboard[0][idx].text = "{} {}".format(number, emoji)

    return keyboard

def subscribe(bot, update):

    global data
    data = load_data()
    chats = [x["id"] for x in data["chats"]]
    if update.effective_chat.id not in chats:
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

global data
data = load_data()

emojis = ["👍","😂","😍","🙈"]
keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(i, callback_data=i) for i in emojis]])
