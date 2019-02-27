# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4
import quickstart
import time
import datetime

from telegram.utils.helpers import escape_markdown

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler

import logging

import db
import piikki

ALKU, LISAA, NOSTA, OHJAA, POISTA = range(5)
saldo_sanat = ["Näytä saldo 💶👀", "Lisää saldoa 💶⬆️", "Nosta rahaa saldosta 💶⬇️"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
updater = None

#tuotanto
#BOT_TOKEN = "647159337:AAFmV4Rf5tJ5nTdWHUEa1qFH1yxzK10r4PE"
#CHAT_ID = -386083933 #the id of the chat where you want the messages to be forwarded
# testi
BOT_TOKEN = "795847607:AAFVVYCqMnULe22gDNlQjPVMzCcxibKWric"
CHAT_ID = -393042631 #the id of the chat where you want the messages to be forwarded
TO_WHOM = "Kiltistoimareille" #who you are
GRAPHICAL_MANUAL = "AgADBAADMq8xG9nUAVI_RtZ5vEGqlCdEuhoABBZdb5JVge3pB_gGAAEC" #the address of the graphical manual image


confirmation_message = TO_WHOM + " lähetetty: "
#history to enable replying
sent_messages = {}
# events = quickstart.main()
last_events = 0#time.time()

#read the manual file
with open("ohje.txt", "r") as f:
    manual = f.read()

def send_to_raati(update):
    """Send an inline message to receiving chat"""

    global updater
    u = update.chosen_inline_result
    result_id = u.result_id
    user_str = '<b>Anonymous</b>'
    if result_id != 'anonymous':
        from_user = u.from_user
        if from_user:
            user_str = '{} {}'.format(from_user.first_name, from_user.last_name)
            if from_user.username:
                user_str = '<b>{} (</b>@{}<b>)</b>'.format(user_str, from_user.username)
    message = '{}\n{}'.format(user_str, u.query)
    updater.bot.send_message(
        CHAT_ID,
        message,
        parse_mode='HTML'
    )


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    print(update)
    # update.message.reply_text('Hi!')


def inlinequery(bot, update):
    """Handle the inline query."""

    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id='normal',
            title="Lähetä " + TO_WHOM,
            input_message_content=InputTextMessageContent(confirmation_message + query)),
        InlineQueryResultArticle(
            id='anonymous',
            title="Lähetä {} anonyyminä".format(TO_WHOM),
            input_message_content=InputTextMessageContent(confirmation_message + query)),
    ]
    update.inline_query.answer(results)


def inlineresult(bot, update):
    """Test if the message is empty and call the function the forwards the message to the receiving chat"""

    if(len(update.chosen_inline_result.query.strip()) > 0):
        send_to_raati(update)


def error(bot, update, error):
    """Log Errors caused by Updates."""

    logger.warning('Update "%s" caused error "%s"', update, error)


def help(bot, update):
    """Send help"""

    bot.send_message(
        update.effective_chat.id,
        manual,
        parse_mode = "HTML")


def kuva(bot, update):
    """Send graphical help"""

    if GRAPHICAL_MANUAL:
        bot.send_photo(update.effective_chat.id, GRAPHICAL_MANUAL)
    else:
        bot.send_message(update.effective_chat.id, "Kuvaa ei saatavilla")


def robust_send_message(bot, msg, to, reply_id):
    """A robust method for forwarding different types of messages anonymously"""

    sent = None

    if msg.text:
        if not msg.text.startswith(confirmation_message.strip()):
            sent = bot.send_message(to, msg.text, reply_to_message_id = reply_id)
        else:
            bot.send_message(msg.chat.id, "Huomaa, että anonyymeihin inline-viesteihin ei voi vastata :)")
    elif msg.sticker:
        sent = bot.send_sticker(to, msg.sticker.file_id, reply_to_message_id = reply_id)
    elif msg.photo:
        sent = bot.send_photo(to, msg.photo[0].file_id, msg.caption, reply_to_message_id = reply_id)
    elif msg.video:
        sent = bot.send_video(to, msg.video.file_id, msg.caption, reply_to_message_id = reply_id)
    elif msg.video_note:
        sent = bot.send_video_note(to, msg.video_note.file_id, reply_to_message_id = reply_id)
    elif msg.document:
        sent = bot.send_document(to, msg.document.file_id, reply_to_message_id = reply_id)
    elif msg.voice:
        sent = bot.send_voice(to, msg.voice.file_id, reply_to_message_id = reply_id)
    elif msg.audio:
        sent = bot.send_audio(to, msg.audio.file_id, reply_to_message_id = reply_id)
    elif msg.location:
        sent = bot.send_location(to, location = msg.location, reply_to_message_id = reply_id)
    else:
        bot.send_message(msg.chat.id, "Tiedostomuoto ei ole tuettu :(")

    return sent


def send_from_private(bot, update):
    """Forward a private message sent for the bot to the receiving chat anonumously"""

    msg = update.effective_message
    sent_message = robust_send_message(bot, msg, CHAT_ID, None)
    sent_messages[sent_message.message_id] = (msg.chat.id, msg.message_id)


def reply(bot, update):
    """Forward reply from receiving chat back to the original sender"""

    id = update.effective_message.reply_to_message.message_id
    if id in sent_messages:
        org = sent_messages[id]
        robust_send_message(bot, update.effective_message, org[0], org[1])

def tapahtumat(bot, update):
    global events
    global last_events
    if time.time() - last_events > 600:
        events = quickstart.main()
        last_events = time.time()

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
    global events
    global last_events
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

def main():
    # Create the Updater and pass it your bot's token.
    global updater, saldo_sanat
    updater = Updater(token = BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    poisto_handler = ConversationHandler(
        entry_points = [CommandHandler("poista_edellinen", piikki.poistatko, Filters.private)],
        states = {
            POISTA: [MessageHandler(Filters.text, piikki.poista)]
        },
        fallbacks = [CommandHandler("lopeta", piikki.lopeta)]
    )

    saldo_handler = ConversationHandler(
        entry_points = [CommandHandler("saldo", piikki.saldo, Filters.private)],
        states = {
            ALKU: [MessageHandler(Filters.text, piikki.saldo)],
            OHJAA: [RegexHandler('^({}|{}|{})$'.format(saldo_sanat[0], saldo_sanat[1], saldo_sanat[2]), piikki.ohjaa)],
            LISAA: [MessageHandler(Filters.text, piikki.lisaa)],
            NOSTA: [MessageHandler(Filters.text, piikki.nosta)],
        },
        fallbacks = [CommandHandler("lopeta", piikki.lopeta)]

    )
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(saldo_handler)
    dp.add_handler(poisto_handler)
    #send the manual when user sends /help
    dp.add_handler(CommandHandler("help", help, Filters.private))

    #send the graphic manual when user sends /kuva
    dp.add_handler(CommandHandler("kuva", kuva, Filters.private))

    dp.add_handler(CommandHandler("tapahtumat", tapahtumat))

    dp.add_handler(CommandHandler("tanaan", tanaan_command))

    dp.add_handler(CommandHandler("store", piikki.store, Filters.private))

    dp.add_handler(CommandHandler("rekisteroidy", piikki.rekisteroidy, Filters.private))

    dp.add_handler(CallbackQueryHandler(piikki.button))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(ChosenInlineResultHandler(inlineresult))

    # log all errors
    dp.add_error_handler(error)

    #forward private messages to the receiving group
    dp.add_handler(MessageHandler(Filters.private, send_from_private))

    #if message sent to the receiving group is a reply to a private message sent by this bot
    #the bot will forward the reply to the original sender
    dp.add_handler(MessageHandler(Filters.reply, reply))

    dp.add_handler(MessageHandler(Filters.text, tanaan_text))


    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
