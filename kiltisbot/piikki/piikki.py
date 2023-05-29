# coding=utf-8

"""Contains all the functions to use the tab functionality of Kiltisbot.
"""

import datetime
import math

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
 InlineQueryResultArticle, InputTextMessageContent, ChosenInlineResult, Update)
import telegram
from telegram.ext import (ExtBot, Job, Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler,
  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, StringRegexHandler)
from telegram.ext import filters
from ..utils import CallbackContext as CbCtx

import config
from kiltisbot import db, fiirumi
from kiltisbot.strings import TAB_INSTRUCTIONS_MSG, TAB_INSTRUCTIONS_IN_ENGLISH_MSG, TERMS_OF_USE_MSG


ALKU, LISAA, NOSTA, OHJAA, POISTA, HYVAKSYN = range(6)
saldo_sanat = ["Näytä saldo 💶👀", "Lisää saldoa 💶⬆️", "Nosta rahaa saldosta 💶⬇️"]


async def store(update: Update, context: CbCtx):
    """Handles the "kauppa" commad for the bot. Prints the products as buttons that can be used to buy products."""

    if not await is_registered(context.bot, update):
        return
    products = db.get_items()
    y = 2
    x = math.ceil(len(products) / y)
    keyboard = [[]]
    for i in range(x):
        row = []
        for j in range(y):
            if j + i*y < len(products):
                prod = products[j + i*y][0]
                price = products[j + i*y][1] / 100
                btn = InlineKeyboardButton("{} {:.2f}€".format(prod, price), callback_data = prod)
                row.append(btn)
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Poistu", callback_data="Poistu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text('Mitä laitetaan?', reply_markup=reply_markup)


async def button(update: Update, context: CbCtx):
    """Callback funtion for the inline keyboard buttons that handles what happens when user chooses an option in the store."""
    assert update.callback_query is not None, "Update unexpectedly has no callback_query"
    assert update.callback_query.data is not None, "Update unexpectedly has no callback_query.data"
    if update.callback_query.data.split(" ")[-1] in fiirumi.emojis:
        await fiirumi.vote_message(context.bot, update)
        return
    if not await is_registered(context.bot, update):
        return
    query = update.callback_query
    if query.data == "Poistu":
        await query.edit_message_text(text="Osto keskeytetty")
        return
    assert update.effective_user is not None, "No user in update"
    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    price = db.get_price(query.data)
    name = db.get_user(user)[0][2]

    db.add_transaction(user, name, query.data, time, price)
    db.update_balance(user, -price)
    db.update_stock(query.data, -1)

    saldo = db.get_balance(user)
    await query.edit_message_text(text="Ostit tuotteen: {}.\n\nSaldo: {:.2f}€".format(query.data, saldo / 100))


async def rekisteroidy(update: Update, context: CbCtx):
    """Handles the conversations when registering new customers."""
    assert update.effective_user is not None, "No user in update"
    assert update.effective_chat is not None, "No chat in update"
    user = update.effective_user.id
    if len(db.get_user(user)) > 0:
        await context.bot.send_message(update.effective_chat.id, "Olet jo käyttäjä.")
        return ConversationHandler.END
    else:
        keyboard = [["Kyllä"], ["Ei"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)
        assert update.message is not None, "Update unexpectedly has no message"
        await update.message.reply_text(TERMS_OF_USE_MSG, reply_markup=reply_markup, parse_mode = "HTML")
    return HYVAKSYN


async def hyvaksyn(update: Update, context: CbCtx):
    """Conversation handler for when the user accepts terms and conditions."""
    assert update.message is not None, "Update unexpectedly has no message"
    user = update.effective_user
    assert user is not None, "No user in update"
    assert update.effective_chat is not None, "No chat in update"
    if update.message.text == "Kyllä":
        name = ""
        if user.first_name and user.last_name:
            name = "{} {}".format(user.first_name, user.last_name)
        else:
            name = user.first_name

        nick = ""
        if user.username:
            nick = user.username

        db.add_user(user.id, nick, name, 30)

        await context.bot.send_message(update.effective_chat.id, "Onneksi olkoon! Sinut on nyt lisätty käyttäjäksi. Kirjoittamalla /piikki_ohje näet mitä kaikkea sähköisellä piikillä voi tehdä.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await context.bot.send_message(update.effective_chat.id, "Ei se mitään, paperinen piikki on myös ihan okei. Minä odottelen täällä jos muutatkin mielesi :)", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

async def saldo(update: Update, context: CbCtx):
    """Conversations handler for when the user wishes to alter their saldo."""

    if not await is_registered(context.bot, update):
        return
    assert update.message is not None, "Update unexpectedly has no message"
    assert update.effective_user is not None, "No user in update"
    global saldo_sanat
    keyboard = [[saldo_sanat[1]], [saldo_sanat[2]]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)
    saldo = db.get_balance(update.effective_user.id) / 100
    await update.message.reply_text('Saldosi on {:.2f}€.\n\nMitä haluaisit tehdä?\n\nKirjoita missä vaiheessa tahansa /lopeta keskeyttäksesi toiminnon.'.format(saldo), reply_markup=reply_markup)
    breakpoint()
    return OHJAA

async def ohjaa(update: Update, context: CbCtx):
    """"Conversation handler for when the user wants to top up or withdraw from their account."""
    global saldo_sanat
    assert update.message is not None, "Update unexpectedly has no message"
    assert update.effective_message is not None, "No message in update"
    assert update.effective_user is not None, "No user in update"
    assert update.effective_chat is not None, "No chat in update"
    print(update.effective_message.text)
    if update.effective_message.text == saldo_sanat[0]:
        saldo = db.get_balance(update.effective_user.id)
        await context.bot.send_message(update.effective_chat.id, "Saldosi on {:.2f}€.".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    elif update.effective_message.text == saldo_sanat[1]:
        await update.message.reply_text("Paljonko saldoa haluaisit lisätä? Anna positiivinen desimaaliluku.", reply_markup = ReplyKeyboardRemove())
        return LISAA

    elif update.effective_message.text == saldo_sanat[2]:
        await update.message.reply_text("Paljonko rahaa haluaisit nostaa saldosta? Anna positiivinen desimaaliluku.", reply_markup = ReplyKeyboardRemove())
        return NOSTA
    else:
        return ConversationHandler.END

async def lisaa(update: Update, context: CbCtx):
    """Add money to account."""

    maara = 0
    assert update.message is not None, "Update unexpectedly has no message"
    assert update.effective_user is not None, "No user in update"
    assert update.message.text is not None, "Message unexpectedly has no text"  # TODO: send error message to user when this happens and require a number
    try:
        maara = int(float(update.message.text.replace(",", ".")) * 100)
        if maara < 0:
            raise ValueError
    except ValueError:
        await context.bot.send_message(update.message.chat.id, "Antamasi luku ei kelpaa. Lisääminen keskeytetty.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END
    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    name = db.get_user(user)[0][2]

    db.update_balance(update.effective_user.id, maara)
    db.add_transaction(user, name, "PANO", time, maara)

    saldo = db.get_balance(update.effective_user.id)
    await context.bot.send_message(update.message.chat.id, "Saldon lisääminen onnistui. Saldosi on nyt {:.2f}€".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

async def nosta(update: Update, context: CbCtx):
    """Withdraw money from account."""

    maara = 0
    assert update.message is not None, "Update unexpectedly has no message"
    assert update.message.text is not None, "Message unexpectedly has no text"  # TODO: send error message to user when this happens and require a number
    assert update.effective_user is not None, "No user in update"
    try:
        maara = int(float(update.message.text.replace(",", ".")) * 100)
        if maara < 0:
            raise ValueError
    except ValueError:
        await context.bot.send_message(update.message.chat.id, "Antamasi luku ei kelpaa. Nosto keskeytetty.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END
    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    name = db.get_user(user)[0][2]

    db.update_balance(update.effective_user.id, -maara)
    db.add_transaction(user, name, "NOSTO", time, maara)

    saldo = db.get_balance(update.effective_user.id)
    await context.bot.send_message(update.message.chat.id, "Rahan nostaminen saldosta onnistui. Saldosi on nyt {:.2f}€".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

async def lopeta(update: Update, _context: CbCtx):
    """Handles ending a conversations handler conversations using command /lopeta."""
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text('Toiminto keskeytetty.', reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

async def ei_lopetettavaa(update: Update, _context: CbCtx):
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text('Sinulla ei ollut käynnissä toimintoa, jonka voisi lopettaa.', reply_markup = ReplyKeyboardRemove())

async def tuntematon(update: Update, _context: CbCtx):
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text('Odottamaton komento. Toiminto keskeytetty.', reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

async def poistatko(update: Update, context: CbCtx):
    """Handles removing the last action made by the user."""

    if not await is_registered(context.bot, update):
        return
    keyboard = [["Kyllä"],[ "Ei"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)
    assert update.effective_user is not None, "No user in update"
    edellinen = db.get_last_transaction(update.effective_user.id)
    aika = edellinen[5][:16].split("T")
    paiva = aika[0]
    aika = aika[1]
    tuote = edellinen[3]
    hinta = edellinen[4] / 100
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text("""Haluatko todella poistaa tapahtuman:\n{}  {}   {}   {:.2f}€?\n\nKirjoita missä vaiheessa tahansa /lopeta keskeyttääksesi toiminnon.""".format(paiva, aika, tuote, hinta), reply_markup=reply_markup)
    return POISTA


async def poista(update: Update, context: CbCtx):
    """Does the actual removing when user wants to remove their last action."""
    assert update.message is not None, "Update unexpectedly has no message"
    assert update.effective_user is not None, "No user in update"
    if update.message.text == "Kyllä":
        user = update.effective_user.id
        edellinen = db.get_last_transaction(update.effective_user.id)
        print("Removing transaction: ", edellinen[0])
        summa = -edellinen[4] if edellinen[3] == "PANO" else edellinen[4]
        if edellinen[3] != "PANO" and edellinen[3] != "NOSTO":
            try:
                db.update_stock(edellinen[3], 0)
            except TypeError:
                pass
        db.update_balance(user, summa)
        db.delete_transaction(edellinen[0])
        saldo = db.get_balance(user)
        await context.bot.send_message(update.message.chat.id, "Tapahtuma poistettu. Tilisi saldo on {:.2f}€.".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
    else:
        await context.bot.send_message(update.message.chat.id, "Tapahtumaa ei poistettu", reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END


async def hinnasto(update: Update, context: CbCtx):
    """Prints items in stock and their prices."""
    assert update.message is not None, "Update unexpectedly has no message"
    items = db.get_items()
    text = "```\nHinnasto:\n"
    for i in items:
        text += "{:_<18.18} {:.2f}€\n".format(i[0].strip() + " ", i[1] /100)
    await context.bot.send_message(update.message.chat.id, text + "```", parse_mode="MARKDOWN")


async def ohje(update: Update, context: CbCtx):
    assert update.effective_user is not None, "No user in update"
    await context.bot.send_message(update.effective_user.id, TAB_INSTRUCTIONS_MSG, parse_mode = "HTML")


async def ohje_in_english(update: Update, context: CbCtx):
    assert update.effective_user is not None, "No user in update"
    await context.bot.send_message(update.effective_user.id, TAB_INSTRUCTIONS_IN_ENGLISH_MSG, parse_mode = "HTML")


# TODO can not export twice during the same minute because we would get same sheet name
async def export_users(update: Update, context: CbCtx):
    """Export users to Google sheets."""

    if await is_admin(context.bot, update):
        users = db.drive.export_users()
        assert update.message is not None, "Update unexpectedly has no message"
        await context.bot.send_message(update.message.chat.id, "Käyttäjien vieminen onnistui!\n\n{} käyttäjää yhteensä.".format(users))


async def export_transactions(update: Update, context: CbCtx):
    """Export sales events to Google sheets."""

    if await is_admin(context.bot, update):
        trans = db.drive.export_transactions()
        assert update.message is not None, "Update unexpectedly has no message"
        await context.bot.send_message(update.message.chat.id, "Tapahtumien vieminen onnistui!\n\n{} uutta tapahtumaa.".format(trans))


# TODO exporting invetory to empty sheet doesn't create names row for products in sheet. This
# could be fixed same time when maara field is removed from database.
async def export_inventory(update: Update, context: CbCtx):
    """Exports current inventory to google sheets."""
    if await is_admin(context.bot, update):
        db.drive.export_inventory()
        assert update.message is not None, "Update unexpectedly has no message"
        await context.bot.send_message(update.message.chat.id, "Tuotteiden vieminen onnistui!")


async def import_inventory(update: Update, context: CbCtx):
    """Import inventory from Google sheets."""

    if await is_admin(context.bot, update):
        items = db.drive.import_inventory()
        assert update.message is not None, "Update unexpectedly has no message"
        await context.bot.send_message(update.message.chat.id, "Tuotteiden tuominen onnistui!\n\n{} tuotetta yhteensä.".format(items) )


async def import_users(update: Update, context: CbCtx):
    """Import users from Google Sheets. BE CAREFUL WHEN USING THIS. THIS WILL OWERWIRTE YOUR DATABASE!"""

    if await is_admin(context.bot, update):
        delta = db.drive.import_users()
        message = "Käyttäjiä lisätty {}".format(delta) if delta >= 0 else "Käyttäjiä poistettu {}".format(abs(delta))
        assert update.message is not None, "Update unexpectedly has no message"
        await context.bot.send_message(update.message.chat.id, "Käyttäjien tuominen onnistui! \n\n" + message)


async def import_transactions(update: Update, context: CbCtx):
    """Import transactions from Google Sheets. BE CAREFUL WHEN USING THIS. THIS WILL OWERWRITE YOUR DATABASE!"""

    # TODO: other imports have their safety exports defined in drive.py
    #safety export of transactions
    #export_transactions(context.bot, update)

    if await is_admin(context.bot, update):
        delta = db.drive.import_transactions()
        message = "Tapahtumia tuotu {}".format(delta)
        assert update.message is not None, "Update unexpectedly has no message"
        await context.bot.send_message(update.message.chat.id, "Tapahtumien tuominen onnistui! \n\n" + message)


async def backup(context: CbCtx):
    """Backs up all the things to Google sheets."""

    users = db.drive.export_users()
    transactions = db.drive.export_transactions()
    db.drive.export_inventory()

    await context.bot.send_message(config.ADMIN_CHAT, "Backup tehty! \n{} käyttäjää. \n{} uutta tapahtumaa.".format(users, transactions))


async def kulutus(context: CbCtx):
    """Prints the daily tab events to the group chat."""
    eilinen = (datetime.datetime.now() - datetime.timedelta(days = 1)).isoformat()
    tuotteet = db.get_consumption_after(eilinen)
    text = "```\nEdellisen päivän kulutus:\n"
    for i in tuotteet:
        text += "{:_<18.18}{:2d} kpl\n".format(i[0].strip() + " ", i[1])

    await context.bot.send_message(config.ADMIN_CHAT, text + "```", parse_mode="MARKDOWN")


async def velo(update: Update, context: CbCtx):
    """Encourages people who are more than 5€ negative in their tab to pay their debts."""

    if await is_admin(context.bot, update):
        velalliset = db.get_velalliset()
        for i in velalliset:
            await context.bot.send_photo(i[0], open("assets/img/velat.jpg", "rb"))


async def is_registered(bot, update: Update):
    """Check if user is registered."""
    user = update.effective_user
    assert user is not None, "Update does not have effective_user"
    if len(db.get_user(user.id)) < 1:
        assert update.message is not None, "Update does not have message"
        bot.send_message(update.message.chat.id, "Rekisteröidy käyttääksesi tätä toiminnallisuutta kirjoittamalla /kirjaudu.")
        return False
    else:
        return True

async def is_admin(bot: ExtBot, update: Update):
    """Check if user is admin."""
    if update.effective_user is None:
        raise ValueError("Update does not have effective_user")

    if update.effective_user.id in config.BOT_ADMINS:
        return True
    else:
        if update.message is None:
            raise ValueError("Update does not have message")
        await bot.send_message(update.message.chat.id, "You are not authorized.")
        return False

#ConversationHandler function that handles the conversation for deleting previous action.
poisto_handler = ConversationHandler(
    entry_points = [CommandHandler("poista_edellinen", poistatko, filters.ChatType.PRIVATE)],
    states = {
        POISTA: [MessageHandler(filters.Regex(r'^(Kyllä|Ei)$'), poista)]
    },
    fallbacks = [CommandHandler("lopeta", lopeta), MessageHandler(filters.ALL, tuntematon)],
    allow_reentry = True
)

#ConversationHandler function that handles the conversation for topping up or withdrawing money from account.
# TODO: now if user inputs /lopeta after she has pressed "lisää" or "nosta" process is terminated with
# message "Sinulla ei ollut käynnissä toimintoa, jonka voisi lopettaa". More correct would be "Toiminto keskeytetty".
saldo_handler = ConversationHandler(
    entry_points = [CommandHandler("saldo", saldo, filters.ChatType.PRIVATE)],
    states = {
        ALKU: [MessageHandler(filters.TEXT, saldo)],
        OHJAA: [MessageHandler(filters.Regex('^({}|{}|{})$'.format(saldo_sanat[0], saldo_sanat[1], saldo_sanat[2])), ohjaa)],
        LISAA: [MessageHandler(filters.TEXT, lisaa)],
        NOSTA: [MessageHandler(filters.TEXT, nosta)],
    },
    fallbacks = [CommandHandler("lopeta", lopeta), MessageHandler(filters.ALL, tuntematon)],
    allow_reentry = True

)

#Conversation handler function that handles the conversation for registering as an user.
register_handler = ConversationHandler(
    entry_points = [CommandHandler("kirjaudu", rekisteroidy, filters.ChatType.PRIVATE)],
    states = {
        HYVAKSYN: [MessageHandler(filters.ALL, hyvaksyn)]
    },
    fallbacks = [CommandHandler("lopeta", lopeta),  MessageHandler(filters.ALL, tuntematon)]
)
