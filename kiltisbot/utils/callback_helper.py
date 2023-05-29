from logging import Logger
from typing import Awaitable, Callable

from telegram import Message, Update
from telegram.ext import CallbackContext, ExtBot


logger = Logger(__name__)

CallbackContext = CallbackContext[ExtBot, dict, dict, dict]


def msg_callback(fun: Callable[[Message, CallbackContext], Awaitable[None]]) -> Callable[[Update, CallbackContext], Awaitable[None]]:
    """Converts a function that takes a Message and CallbackContext as arguments
    to a function that takes an Update and CallbackContext as arguments.
    """
    async def callback(update: Update, context: CallbackContext):
        if update.message is None:
            logger.warning("Message callback called with update that has no message")
            return
        await fun(update.message, context)
    return callback

