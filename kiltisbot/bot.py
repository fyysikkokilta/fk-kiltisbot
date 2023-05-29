"""
To make kiltisbotti alive run: $ python3 bot.py
"""

import datetime
import logging


from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
)
from telegram.ext import filters
from telegram import Update

import config
from kiltisbot import (
    fiirumi,
    fkcal,
    msg,
    piikki,
    utils,
)
from kiltisbot.strings import START_MSG, HELP_MSG, HELP_IN_ENGLISH_MSG
from .utils import CallbackContext

logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext):
    """First message users see after they press /start."""
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text(START_MSG)


async def help_message(update: Update, context: CallbackContext):
    assert update.message is not None
    await update.message.reply_text(HELP_MSG)


async def help_message_in_english(update: Update, context: CallbackContext):
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text(HELP_IN_ENGLISH_MSG)


async def post_init(app: Application):
    jq = app.job_queue
    if jq is None:
        raise Exception("JobQueue is None")
    await utils.flush_messages(app.bot)

    # All command interactions with bot.
    # TODO: more dry way to do this?
    app.add_handler(CommandHandler("help", help_message, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("help_in_english", help_message_in_english, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", fiirumi.subscribe))
    app.add_handler(CommandHandler("tapahtumat", fkcal.tapahtumat))
    app.add_handler(CommandHandler("tanaan", fkcal.tanaan_command))
    app.add_handler(CommandHandler("messaging_instructions", msg.ohje_in_english, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("viesti_ohje", msg.ohje, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("candy_store", piikki.ohje_in_english, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("export_inventory", piikki.export_inventory, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("export_transactions", piikki.export_transactions, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("export_users", piikki.export_users, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("hinnasto", piikki.hinnasto, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("import_inventory", piikki.import_inventory, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("import_transactions", piikki.import_transactions, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("import_users", piikki.import_users, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("kauppa", piikki.store, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("kulutus", piikki.analytics.send_histogram, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("piikki_ohje", piikki.ohje, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("velo", piikki.velo, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("whoami", utils.whoami))

    # These take care of all "button interactions" with bot.
    app.add_handler(piikki.register_handler)
    app.add_handler(piikki.saldo_handler)
    app.add_handler(piikki.poisto_handler)
    app.add_handler(CallbackQueryHandler(piikki.button))

    # Sending messages to bot & react to "tänään" string. Order matters here.
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE, msg.send_from_private))
    app.add_handler(MessageHandler(filters.REPLY, msg.reply))
    app.add_handler(MessageHandler(filters.TEXT, fkcal.tanaan_text))

    # Backup, check Fiirumi and report admin chat on given intervals.
    jq.run_daily(
        piikki.kulutus,
        time=datetime.time(7, 0, 0),
        name="Kulutus",
    )
    jq.run_daily(piikki.backup, time=datetime.time(7, 0, 0), name="Backup")

    jq.run_repeating(fiirumi.check_messages, interval=5)
    # jq.run_repeating(piikki.kulutus,interval=10, name = "Kulutus", )
    # jq.run_repeating(piikki.backup, interval=10, name = "Backup")

    # NOTE: Please comment out this line when wanting tracebacks in error logs.
    # app.add_error_handler(utils.log_error)
    logger.info("Post init done.")


if __name__ == "__main__":
    app = Application.builder().token(config.BOT_TOKEN).concurrent_updates(False).build()
    app.post_init = post_init
    app.run_polling()
