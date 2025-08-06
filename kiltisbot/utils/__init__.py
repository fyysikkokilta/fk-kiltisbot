"""
Logging settings and come helper functions.
"""

import logging
import time
from telegram import Update
from telegram.ext import ContextTypes


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence automatic logs of running scheduled tasks
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)


async def log_error(update: object | None, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def flush_messages(bot):
    """Flushes the messages send to the bot during downtime so that the bot
    does not start spamming when it gets online again."""

    updates = await bot.get_updates()
    while updates:
        print("Flushing {} messages.".format(len(updates)))
        time.sleep(1)
        updates = await bot.get_updates(updates[-1]["update_id"] + 1)


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return user or chat id depending whether it is called in chat
    or with private message."""
    assert update.effective_message is not None, "Update unexpectedly has no message"

    id = update.effective_message.chat.id
    await context.bot.send_message(id, "Tämän chätin ID on {}".format(id))
