
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult
from telegram.ext import InlineQueryHandler, ChosenInlineResultHandler

#test
#CHAT_ID = -393042631 #the id of the chat where you want the messages to be forwarded
#tuotanto
CHAT_ID = -386083933 #the id of the chat where you want the messages to be forwarded

TO_WHOM = "Kiltistoimareille" #who you are
confirmation_message = TO_WHOM + " lähetetty: "

GRAPHICAL_MANUAL = "AgADBAADMq8xG9nUAVI_RtZ5vEGqlCdEuhoABBZdb5JVge3pB_gGAAEC" #the address of the graphical manual image

sent_messages = {}

with open("ohje.txt", "r") as f:
    manual = f.read()

def ohje(bot, update):
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

def send_to_raati(bot, update):
    """Send an inline message to receiving chat"""

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
    bot.send_message(
        CHAT_ID,
        message,
        parse_mode='HTML'
    )


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
        send_to_raati(bot, update)


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
