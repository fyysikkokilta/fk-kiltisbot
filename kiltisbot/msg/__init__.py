"""
A file that contains all the messaging functionalities of Kiltisbot.
"""

from typing import Optional
from telegram import Message, Update
from telegram.ext import ExtBot, ContextTypes
from kiltisbot import config
from kiltisbot.strings import INSTRUCTIONS_MSG, INSTRUCTIONS_IN_ENGLISH_MSG

# TODO sending non supported message type logs warning
# "'NoneType' object has no attribute 'message_id'"

sent_messages: dict[int, tuple[int, int]] = {}


async def ohje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None, "Update unexpectedly has no chat"
    await context.bot.send_message(update.effective_chat.id, INSTRUCTIONS_MSG, parse_mode="HTML")


async def ohje_in_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None, "Update unexpectedly has no chat"
    await context.bot.send_message(update.effective_chat.id, INSTRUCTIONS_IN_ENGLISH_MSG, parse_mode="HTML")


async def robust_send_message(bot: ExtBot, msg: Message, to: int, reply_id: Optional[int] = None):
    """A robust method for forwarding different types of messages anonymously"""
    sent = None
    if msg.text:
        sent = await bot.send_message(to, msg.text, reply_to_message_id=reply_id)
    elif msg.sticker:
        sent = await bot.send_sticker(to, msg.sticker.file_id, reply_to_message_id=reply_id)
    elif msg.photo and msg.caption:
        sent = await bot.send_photo(to, msg.photo[0].file_id, msg.caption, reply_to_message_id=reply_id)
    elif msg.video and msg.caption:
        sent = await bot.send_video(to, msg.video.file_id, caption=msg.caption, reply_to_message_id=reply_id)
    elif msg.video_note:
        sent = await bot.send_video_note(to, msg.video_note.file_id, reply_to_message_id=reply_id)
    elif msg.document:
        sent = await bot.send_document(to, msg.document.file_id, reply_to_message_id=reply_id)
    elif msg.voice:
        sent = await bot.send_voice(to, msg.voice.file_id, reply_to_message_id=reply_id)
    elif msg.audio:
        sent = await bot.send_audio(to, msg.audio.file_id, reply_to_message_id=reply_id)
    elif msg.location:
        sent = await bot.send_location(to, location=msg.location, reply_to_message_id=reply_id)
    else:
        await bot.send_message(msg.chat.id, "Tiedostomuoto ei ole tuettu :(")

    return sent


async def send_from_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward a private message sent for the bot to the receiving chat anonumously"""
    msg = update.effective_message
    assert msg is not None, "Update unexpectedly has no message"
    sent_message = await robust_send_message(context.bot, msg, config.MESSAGING_CHAT, None)
    assert sent_message is not None, "Message was not sent"
    sent_messages[sent_message.message_id] = (msg.chat.id, msg.message_id)


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward reply from receiving chat back to the original sender"""
    assert update.effective_message is not None, "Update unexpectedly has no message"
    assert update.effective_message.reply_to_message is not None, "Update message isn't a reply"

    id = update.effective_message.reply_to_message.message_id
    if id in sent_messages:
        org = sent_messages[id]
        await robust_send_message(context.bot, update.effective_message, org[0], org[1])
