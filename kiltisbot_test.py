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
import time


from telegram.utils.helpers import escape_markdown

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler

import logging

import db
import piikki
import kalenteri
import msg

ALKU, LISAA, NOSTA, OHJAA, POISTA, HYVAKSYN= range(6)
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
GRAPHICAL_MANUAL = "AgADBAADMq8xG9nUAVI_RtZ5vEGqlCdEuhoABBZdb5JVge3pB_gGAAEC" #the address of the graphical manual image


#history to enable replying

#read the manual file
with open("ohje.txt", "r") as f:
    manual = f.read()

def start(bot, update):
    """Send a message when the command /start is issued."""
    print(update)
    update.message.reply_text('Heippa! Kirjoita /help, niin näet, mitä kaikea osaan tehdä!')



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


def main():
    
    global updater, saldo_sanat
    updater = Updater(token = BOT_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(piikki.saldo_handler)
    dp.add_handler(piikki.poisto_handler)
    dp.add_handler(piikki.register_handler)

    dp.add_handler(CommandHandler("help",          help, Filters.private))
    dp.add_handler(CommandHandler("kuva",          kuva, Filters.private))

    dp.add_handler(CommandHandler("tapahtumat",    kalenteri.tapahtumat))
    dp.add_handler(CommandHandler("tanaan",        kalenteri.tanaan_command))
    
    dp.add_handler(CommandHandler("kauppa",        piikki.store, Filters.private))
    dp.add_handler(CommandHandler("kirjaudu",      piikki.rekisteroidy, Filters.private))
    dp.add_handler(CommandHandler("commands",      piikki.commands, Filters.private))
    dp.add_handler(CommandHandler("hinnasto",      piikki.hinnasto, Filters.private))
    dp.add_handler(CommandHandler("komennot",      piikki.komennot, Filters.private))
    dp.add_handler(CommandHandler("piikki_ohje",   piikki.ohje, Filters.private))
    dp.add_handler(CommandHandler("lopeta",        piikki.ei_lopetettavaa, Filters.private))
    
    dp.add_handler(CommandHandler("export_users",        piikki.export_users, Filters.private))
    dp.add_handler(CommandHandler("export_transactions", piikki.export_transactions, Filters.private))
    dp.add_handler(CommandHandler("export_inventory",    piikki.export_inventory, Filters.private))
    dp.add_handler(CommandHandler("import_inventory",    piikki.import_inventory, Filters.private))
    dp.add_handler(CommandHandler("velo",                piikki.velo, Filters.private))

    dp.add_handler(MessageHandler(Filters.private, msg.send_from_private))
    dp.add_handler(MessageHandler(Filters.reply, msg.reply))
    dp.add_handler(MessageHandler(Filters.text, kalenteri.tanaan_text))

    dp.add_handler(CallbackQueryHandler(piikki.button))

    dp.add_handler(InlineQueryHandler(msg.inlinequery))
    dp.add_handler(ChosenInlineResultHandler(msg.inlineresult))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
