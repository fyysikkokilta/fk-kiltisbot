"""
Logging settings and come helper functions.
"""

import logging
import time


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence automatic logs of running scheduled tasks
logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)


def log_error(update, context):
    """Log Errors caused by Updates."""

    logger.warning('Update "%s" caused error "%s"', update, context.error)


def flush_messages(bot):
    """Flushes the messages send to the bot during downtime so that the bot
    does not start spamming when it gets online again."""

    updates = bot.get_updates()
    while updates:
        print("Flushing {} messages.".format(len(updates)))
        time.sleep(1)
        updates = bot.get_updates(updates[-1]["update_id"] + 1)


def whoami(update, context):
    """Return user or chat id depending whether it is called in chat
    or with private message."""

    id = update.effective_message.chat.id
    context.bot.send_message(id, "Tämän chätin ID on {}".format(id))
