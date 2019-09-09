"""This file handles getting the events from the Guild of Physics Google calendar and using the bot to send the to the user."""

import quickstart
import datetime
import time

events = quickstart.main()
last_events = time.time()


def tapahtumat(bot, update):
    global last_events, events
    if time.time() - last_events > 600:
        events = quickstart.main()
        last_events = time.time()

    text = ""
    for x,y in events.items():
        text = text + "\n*" + x + "*\n"
        for i in y:
            if len(i) == 1:
                text = text + i[0] + "\n"
            else:
                text = text + "{} [{}]({})\n".format(".".join(i[0].split("-")[::-1]), i[1], i[2])
                #text += "{} {}\n".format(".".join(i[0].split("-")[::-1]), i[1])
    bot.send_message(update.effective_chat.id, text, parse_mode = "MARKDOWN")

def tanaan_command(bot, update):
    tanaan(bot, update, True)

def tanaan_text(bot, update):
    if "tänään" in update.effective_message.text.lower():
        tanaan(bot, update, False)

def tanaan(bot, update, command):
    global last_events, events
    if time.time() - last_events > 600:
        events = quickstart.main()
        last_events = time.time()

    text = "<b>TÄNÄÄN:</b>\n"

    tanaan = datetime.datetime.today().isoformat()[:10] # 'Z' indicates UTC time

    for x, y in events.items():
        for i in y:
            if i[0] == tanaan:
                text += "<a href=\"{}\">{}</a>\n".format(i[2], i[1])

    if not command and text == "<b>TÄNÄÄN:</b>\n":
        return
    elif text == "<b>TÄNÄÄN:</b>\n":
        text = "<b>TÄNÄÄN</b> ei ole tapahtumia"
        bot.send_message(update.effective_chat.id, text, parse_mode = "HTML")
    else:
        bot.send_message(update.effective_chat.id, text, parse_mode = "HTML")
