
import quickstart
import datetime


def tapahtumat(bot, update):

    events = quickstart.main()

    text = ""
    for x,y in events.items():
        text = text + "\n<b>" + x + "</b>\n"
        for i in y:
            if len(i) == 1:
                text = text + i[0] + "\n"
            else:
                text = text + "{} <a href=\"{}\">{}</a>\n".format(".".join(i[0].split("-")[::-1]), i[2], i[1])

    bot.send_message(update.effective_chat.id, text, parse_mode = "HTML")

def tanaan_command(bot, update):
    tanaan(bot, update, True)

def tanaan_text(bot, update):
    if "tänään" in update.effective_message.text.lower():
        tanaan(bot, update, False)

def tanaan(bot, update, command):
    
    events = quickstart.main()

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
