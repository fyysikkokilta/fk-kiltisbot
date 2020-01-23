# -*- coding: utf-8 -*-

import requests
import json
import datetime



data_file = "fiirumi_data.json"
data = load_data(data_file)


def get_posts_after(time):
    """
    Get posts from Fiirumi that are created after the given time in UTC.
    """
    url = "https://fiirumi.fyysikkokilta.fi/posts.json"
    res = requests.get(url)
    data = json.loads(res.text)

    posts = [(x["name"], x["username"], x["created_at"], 
              x["topic_title"], x["topic_slug"], x["category_d"]) 
              for x in data["latest_posts"] if data["created_at"] > time]

    return posts

def check_messages(bot):
    global data

    lorina_id = 7
    keyboard = InlineKeyboardMarkup([[👍,😂,😍,🎉,🙈,💩]])

    data = load_data()
    
    posts = get_posts_after(data["previous_messages"])
    data["previous_messages"] = datetime.datetime.utcnow().isoformat()

    for p in posts:
        for c in data["chats"]:
            msg = format_message(p)
            if not (p["category_id"] == lorina_id and c["name"] == "Fyysikkokilta"):
                text = format_message(p)
                bot.send_message(c["id"], text, reply_markup=keyboard, parse_mode="MARKDOWN")

def voting

def format_message(post):

    base_url = "https://fiirumi.fyysikkokilta.fi/t/"
    global data
    user = [x for x in data["users"] if x["username"] == post["username"]]

    emojis = None
    if len(user) == 0:
        data["users"].append({"username": post["username"], "emojis": {}})
        emojis = {}
    else:
        emojis = user[0]["emojis"]

    emoji_string = "".join([str(emojis[key]) for key in emojis])

    text = "Uusi postaus Φiirumilla!\n\n *{}*\n _{}_({} {}) \n\n [Lue koko postaus]({})"
    text = text.format(post["topic_title"], post["name"], post["username"], 
                       emoji_string, base_url + post["topic_slug"])

    return text
    

def subscribe(bot, update):
    global data
    data = load_data()
    data["chats"].append({"name": update.effective_chat.name, "id": update.update.effective_chat.id})
    save_data(data)
    

def load_data():
    global data
    global data_file
    with open(data_file) as d:
        data = json.reads(d.read())


def save_data(data):
    global data_file
    with open(data_file, "w") as d:
        d.write(json.dumps(data))

