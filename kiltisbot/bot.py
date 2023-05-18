"""
To make kiltisbotti alive run: $ python3 bot.py
"""

import datetime

from telegram.utils.helpers import escape_markdown
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler, JobQueue

import config
from kiltisbot import (
    db,
    fiirumi,
    fkcal,
    msg,
    piikki,
    utils,
)
from kiltisbot.strings import START_MSG, HELP_MSG, HELP_IN_ENGLISH_MSG


def start(update, context):
    """First message users see after they press /start."""

    update.message.reply_text(START_MSG)


def help_message(update, context):
    update.message.reply_text(HELP_MSG)


def help_message_in_english(update, context):
    update.message.reply_text(HELP_IN_ENGLISH_MSG)


def main():
    updater = Updater(token = config.BOT_TOKEN)
    dp = updater.dispatcher
    jq = updater.job_queue
    utils.flush_messages(updater.bot)

    # All command interactions with bot.
    # TODO: more dry way to do this?
    dp.add_handler(CommandHandler("help", help_message, Filters.private))
    dp.add_handler(CommandHandler("help_in_english", help_message_in_english, Filters.private))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("subscribe", fiirumi.subscribe))
    dp.add_handler(CommandHandler("tapahtumat", fkcal.tapahtumat))
    dp.add_handler(CommandHandler("tanaan", fkcal.tanaan_command))
    dp.add_handler(CommandHandler("messaging_instructions", msg.ohje_in_english, Filters.private))
    dp.add_handler(CommandHandler("viesti_ohje", msg.ohje, Filters.private))
    dp.add_handler(CommandHandler("candy_store", piikki.ohje_in_english, Filters.private))
    dp.add_handler(CommandHandler("export_inventory", piikki.export_inventory, Filters.private))
    dp.add_handler(CommandHandler("export_transactions", piikki.export_transactions, Filters.private))
    dp.add_handler(CommandHandler("export_users", piikki.export_users, Filters.private))
    dp.add_handler(CommandHandler("hinnasto", piikki.hinnasto, Filters.private))
    dp.add_handler(CommandHandler("import_inventory", piikki.import_inventory, Filters.private))
    dp.add_handler(CommandHandler("import_transactions", piikki.import_transactions, Filters.private))
    dp.add_handler(CommandHandler("import_users", piikki.import_users, Filters.private))
    dp.add_handler(CommandHandler("kauppa", piikki.store, Filters.private))
    dp.add_handler(CommandHandler("kulutus", piikki.analytics.send_histogram, Filters.private))
    dp.add_handler(CommandHandler("piikki_ohje", piikki.ohje, Filters.private))
    dp.add_handler(CommandHandler("velo", piikki.velo, Filters.private))
    dp.add_handler(CommandHandler("whoami", utils.whoami))

    # These take care of all "button interactions" with bot.
    dp.add_handler(piikki.register_handler)
    dp.add_handler(piikki.saldo_handler)
    dp.add_handler(piikki.poisto_handler)
    dp.add_handler(CallbackQueryHandler(piikki.button))

    # Sending messages to bot & react to "tänään" string. Order matters here.
    dp.add_handler(MessageHandler(Filters.private, msg.send_from_private))
    dp.add_handler(MessageHandler(Filters.reply, msg.reply))
    dp.add_handler(MessageHandler(Filters.text, fkcal.tanaan_text))

    # Backup, check Fiirumi and report admin chat on given intervals.
    jq.run_daily(piikki.kulutus, time = datetime.time(7,0,0), context = updater.bot, name = "Kulutus")
    jq.run_daily(piikki.backup, time = datetime.time(7,0,0), context = updater.bot, name = "Backup")
    jq.run_repeating(fiirumi.check_messages, context=updater.bot, interval=60)

    # NOTE: Please comment out this line when wanting tracebacks in error logs.
    dp.add_error_handler(utils.log_error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()