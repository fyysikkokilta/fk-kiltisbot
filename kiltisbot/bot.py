"""
To make kiltisbotti alive run: $ python3 bot.py
"""

import datetime
import logging


from telegram.ext import (
    filters,
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram import Update

from kiltisbot import (
    config,
    fkcal,
    msg,
    piikki,
    newsletter,
    utils,
)
from kiltisbot.strings import START_MSG, HELP_MSG, HELP_IN_ENGLISH_MSG

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """First message users see after they press /start."""
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text(START_MSG)


async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.message is not None
    await update.message.reply_text(HELP_MSG)


async def help_message_in_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    app.add_handler(CommandHandler("tapahtumat", fkcal.tapahtumat))
    app.add_handler(CommandHandler("tanaan", fkcal.tanaan_command))
    app.add_handler(CommandHandler("viikkotiedote", newsletter.viikkotiedote))
    app.add_handler(CommandHandler("weekly", newsletter.weekly))
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.ChatType.CHANNEL, fkcal.tanaan_text))

    # Backup and report admin chat on given intervals.
    jq.run_daily(
        piikki.kulutus,
        time=datetime.time(7, 0, 0),
        name="Kulutus",
    )
    jq.run_daily(piikki.backup, time=datetime.time(7, 0, 0), name="Backup")

    # NOTE: Please comment out this line when wanting tracebacks in error logs.
    # app.add_error_handler(utils.log_error)
    logger.info("Post init done.")


def main():
    app = Application.builder().token(config.BOT_TOKEN).concurrent_updates(False).build()
    app.post_init = post_init
    app.run_polling()


if __name__ == "__main__":
    main()
