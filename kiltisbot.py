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

from telegram.utils.helpers import escape_markdown

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHAT_ID = -386083933
updater = None
confirmation_message = "Kiltistoimareille lähetetty: "

sent_messages = {}

with open("ohje.txt", "r") as f:
    manual = f.read()

def send_to_raati(update):
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
            title="Lähetä kiltistoimareille",
            input_message_content=InputTextMessageContent(confirmation_message + query)),
        InlineQueryResultArticle(
            id='anonymous',
            title="Lähetä kiltistoimareille anonyyminä",
            input_message_content=InputTextMessageContent(confirmation_message + query)),
    ]
    update.inline_query.answer(results)


def inlineresult(bot, update):
    if(len(update.chosen_inline_result.query.strip()) > 0):
        send_to_raati(update)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def help(bot, update):
    bot.sendMessage(
        update.effective_chat.id,
        manual,
        parse_mode = "HTML"
    )

def kuva(bot, update):
    bot.send_photo(
        update.effective_chat.id,
        "AgADBAADMq8xG9nUAVI_RtZ5vEGqlCdEuhoABBZdb5JVge3pB_gGAAEC"
    )

def robust_send_message(bot, msg, to, reply_id):

    sent = None

    if msg.text and not msg.text.startswith(confirmation_message):
        sent = bot.send_message(to, msg.text, reply_to_message_id = reply_id)
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

    return sent

def send_from_private(bot, update):

    msg = update.effective_message
    sent_message = robust_send_message(bot, msg, CHAT_ID, None)
    sent_messages[sent_message.message_id] = (msg.chat.id, msg.message_id)

def reply(bot, update):
    id = update.effective_message.reply_to_message.message_id
    if id in sent_messages:
        org = sent_messages[id]
        robust_send_message(bot, update.effective_message,
                            org[0], org[1])

def main():
    # Create the Updater and pass it your bot's token.
    global updater
    updater = Updater(token = "647159337:AAFmV4Rf5tJ5nTdWHUEa1qFH1yxzK10r4PE")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help", help, Filters.private))

    dp.add_handler(CommandHandler("kuva", kuva, Filters.private))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(ChosenInlineResultHandler(inlineresult))

    # log all errors
    dp.add_error_handler(error)

    dp.add_handler(MessageHandler(Filters.private, send_from_private))

    dp.add_handler(MessageHandler(Filters.reply, reply))
    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
