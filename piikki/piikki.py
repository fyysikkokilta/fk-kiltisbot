# coding=utf-8

"""Contains all the functions to use the tab functionality of Kiltisbot.
"""

import datetime
import math

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
 InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult)
from telegram.ext import (Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler,
  Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler)

import config
import db
import db.drive
import fiirumi
from strings import STOKE_INSTRUCTIONS_MSG, STOKE_INSTRUCTIONS_IN_ENGLISH_MSG, TERMS_OF_USE_MSG


ALKU, LISAA, NOSTA, OHJAA, POISTA, HYVAKSYN = range(6)
saldo_sanat = ["Näytä saldo 💶👀", "Lisää saldoa 💶⬆️", "Nosta rahaa saldosta 💶⬇️"]


def store(bot, update):
    """Handles the "kauppa" commad for the bot. Prints the products as buttons that can be used to buy products."""

    if not is_registered(bot, update):
        return

    products = db.get_items()
    #print(products)

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

    update.message.reply_text('Mitä laitetaan?', reply_markup=reply_markup)

def button(bot, update):
    """Callback funtion for the inline keyboard buttons that handles what happens when user chooses an option in the store."""

    if update.callback_query.data.split(" ")[-1] in fiirumi.emojis:
        fiirumi.vote_message(bot, update)
        return

    if not is_registered(bot, update):
        return

    query = update.callback_query

    if query.data == "Poistu":
        query.edit_message_text(text="Osto keskeytetty")
        return

    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    price = db.get_price(query.data)
    name = db.get_user(user)[0][2]
    #print(price)

    db.add_transaction(user, name, query.data, time, price)
    db.update_balance(user, -price)

    saldo = db.get_balance(user)
    #print(saldo)
    query.edit_message_text(text="Ostit tuotteen: {}.\n\nSaldo: {:.2f}€".format(query.data, saldo / 100))

def rekisteroidy(bot, update):
    """Handles the conversations when registering new customers."""

    user = update.effective_user.id
    if len(db.get_user(user)) > 0:
        bot.send_message(update.effective_chat.id, "Olet jo käyttäjä.")
        return ConversationHandler.END
    else:

        keyboard = [["Kyllä"], ["Ei"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)
        update.message.reply_text(TERMS_OF_USE_MSG, reply_markup=reply_markup, parse_mode = "HTML")

    return HYVAKSYN

def hyvaksyn(bot, update):
    """Conversation handler for when the user accepts terms and conditions."""

    user = update.effective_user
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

        bot.send_message(update.effective_chat.id, "Onneksi olkoon! Sinut on nyt lisätty käyttäjäksi. Kirjoittamalla /piikki_ohje näet mitä kaikkea sähköisellä piikillä voi tehdä.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        bot.send_message(update.effective_chat.id, "Ei se mitään, paperinen piikki on myös ihan okei. Minä odottelen täällä jos muutatkin mielesi :)", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

def saldo(bot, update):
    """Conversations handler for when the user wishes to alter their saldo."""

    if not is_registered(bot, update):
        return

    global saldo_sanat
    keyboard = [[saldo_sanat[1]], [saldo_sanat[2]]]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)

    saldo = db.get_balance(update.effective_user.id) / 100

    update.message.reply_text('Saldosi on {:.2f}€.\n\nMitä haluaisit tehdä?\n\nKirjoita missä vaiheessa tahansa /lopeta keskeyttäksesi toiminnon.'.format(saldo), reply_markup=reply_markup)

    return OHJAA

def ohjaa(bot, update):
    """"Conversation handler for when the user wants to top up or withdraw from their account."""

    global saldo_sanat
    print(update.effective_message.text)
    if update.effective_message.text == saldo_sanat[0]:
        saldo = db.get_balance(update.effective_user.id)
        bot.send_message(update.effective_chat.id, "Saldosi on {:.2f}€.".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    elif update.effective_message.text == saldo_sanat[1]:
        update.message.reply_text("Paljonko saldoa haluaisit lisätä? Anna positiivinen desimaaliluku.", reply_markup = ReplyKeyboardRemove())
        return LISAA

    elif update.effective_message.text == saldo_sanat[2]:
        update.message.reply_text("Paljonko rahaa haluaisit nostaa saldosta? Anna positiivinen desimaaliluku.", reply_markup = ReplyKeyboardRemove())
        return NOSTA
    else:
        return ConversationHandler.END

def lisaa(bot, update):
    """Add money to account."""
    maara = 0
    try:
        maara = int(float(update.message.text.replace(",", ".")) * 100)
        if maara < 0:
            raise ValueError
    except ValueError:
        bot.send_message(update.message.chat.id, "Antamasi luku ei kelpaa. Lisääminen keskeytetty.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    name = db.get_user(user)[0][2]


    db.update_balance(update.effective_user.id, maara)
    db.add_transaction(user, name, "PANO", time, maara)

    saldo = db.get_balance(update.effective_user.id)
    bot.send_message(update.message.chat.id, "Saldon lisääminen onnistui. Saldosi on nyt {:.2f}€".format(saldo / 100), reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END

def nosta(bot, update):
    """Withdraw money from account."""

    maara = 0
    try:
        maara = int(float(update.message.text.replace(",", ".")) * 100)
        if maara < 0:
            raise ValueError
    except ValueError:
        bot.send_message(update.message.chat.id, "Antamasi luku ei kelpaa. Nosto keskeytetty.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    name = db.get_user(user)[0][2]

    db.update_balance(update.effective_user.id, -maara)
    db.add_transaction(user, name, "NOSTO", time, maara)

    saldo = db.get_balance(update.effective_user.id)
    bot.send_message(update.message.chat.id, "Rahan nostaminen saldosta onnistui. Saldosi on nyt {:.2f}€".format(saldo / 100), reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END

def lopeta(bot, update):
    """Handles ending a conversations handler conversations using command /lopeta."""

    update.message.reply_text('Toiminto keskeytetty.', reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

def ei_lopetettavaa(bot, update):
    update.message.reply_text('Sinulla ei ollut käynnissä toimintoa, jonka voisi lopettaa.', reply_markup = ReplyKeyboardRemove())

def tuntematon(bot, update):
    update.message.reply_text('Odottamaton komento. Toiminto keskeytetty.', reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

def poistatko(bot, update):
    """Handles removing the last action made by the user."""

    if not is_registered(bot, update):
        return

    keyboard = [["Kyllä"],[ "Ei"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)

    edellinen = db.get_last_transaction(update.effective_user.id)
    aika = edellinen[5][:16].split("T")
    paiva = aika[0]
    aika = aika[1]
    tuote = edellinen[3]
    hinta = edellinen[4] / 100

    update.message.reply_text("""Haluatko todella poistaa tapahtuman:\n{}  {}   {}   {:.2f}€?\n\nKirjoita missä vaiheessa tahansa /lopeta keskeyttääksesi toiminnon.""".format(paiva, aika, tuote, hinta), reply_markup=reply_markup)

    return POISTA

def poista(bot, update):
    """Does the actual removing when user wants to remove their last action."""
    if update.message.text == "Kyllä":
        user = update.effective_user.id
        edellinen = db.get_last_transaction(update.effective_user.id)
        print(edellinen[0])

        summa = -edellinen[4] if edellinen[3] == "PANO" else edellinen[4]

        if edellinen[3] != "PANO" and edellinen[3] != "NOSTO":
            try:
                db.update_stock(edellinen[3], 0)
            except TypeError:
                pass

        db.update_balance(user, summa)
        db.delete_transaction(edellinen[0])
        saldo = db.get_balance(user)

        bot.send_message(update.message.chat.id, "Tapahtuma poistettu. Tilisi saldo on {:.2f}€.".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
    else:
        bot.send_message(update.message.chat.id, "Tapahtumaa ei poistettu", reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END

def hinnasto(bot, update):
    """Prints items in stock and their prices."""

    items = db.get_items()
    text = "```\nHinnasto:\n"
    for i in items:
        text += "{:_<18.18} {:.2f}€\n".format(i[0].strip() + " ", i[1] /100)
    bot.send_message(update.message.chat.id, text + "```", parse_mode="MARKDOWN")


def ohje(bot, update):
    bot.send_message(update.effective_user.id, STOKE_INSTRUCTIONS_MSG, parse_mode = "HTML")


def ohje_in_english(bot, update):
    bot.send_message(update.effective_user.id, STOKE_INSTRUCTIONS_IN_ENGLISH_MSG, parse_mode = "HTML")


def export_users(bot, update):
    """Export users to Google sheets."""

    if is_admin(bot, update):
        users = db.drive.export_users()
        bot.send_message(update.message.chat.id, "Käyttäjien vieminen onnistui!\n\n{} käyttäjää yhteensä.".format(users))

def export_transactions(bot, update):
    """Export sales events to Google sheets."""

    if is_admin(bot, update):
        trans = db.drive.export_transactions()
        bot.send_message(update.message.chat.id, "Tapahtumien vieminen onnistui!\n\n{} uutta tapahtumaa.".format(trans))

def export_inventory(bot, update):
    """Exports current inventory to google sheets."""
    if is_admin(bot, update):
        db.drive.export_inventory()
        bot.send_message(update.message.chat.id, "Tuotteiden vieminen onnistui!")

def import_inventory(bot, update):
    """Import inventory from Google sheets."""

    if is_admin(bot, update):
        items = db.drive.import_inventory()
        bot.send_message(update.message.chat.id, "Tuotteiden tuominen onnistui!\n\n{} tuotetta yhteensä.".format(items) )

def import_users(bot, update):
    """Import users from Google Sheets. BE CAREFUL WHEN USING THIS. THIS WILL OWERWIRTE YOUR DATABASE!"""

    if is_admin(bot, update):
        delta = db.drive.import_users()
        message = "Käyttäjiä lisätty {}".format(delta) if delta >= 0 else "Käyttäjiä poistettu {}".format(abs(delta))
        bot.send_message(update.message.chat.id, "Käyttäjien tuominen onnistui! \n\n" + message)

def import_transactions(bot, update):
    """Import transactions from Google Sheets. BE CAREFUL WHEN USING THIS. THIS WILL OWERWRITE YOUR DATABASE!"""

    #safety export of transactions
    export_transactions(bot, update)

    if is_admin(bot, update):
        delta = db.drive.import_transactions()
        message = "Tapahtumia tuotu {}".format(delta)
        bot.send_message(update.message.chat.id, "Tapahtumien tuominen onnistui! \n\n" + message)


def backup(bot, context):
    """Backs up all the things to Google sheets."""

    users = db.drive.export_users()
    transactions = db.drive.export_transactions()
    db.drive.export_inventory()

    bot.send_message(config.ADMIN_CHAT, "Backup tehty! \n{} käyttäjää. \n{} uutta tapahtumaa.".format(users, transactions))


def kulutus(bot, context):
    """Prints the daily tab events to the group chat."""

    eilinen = (datetime.datetime.now() - datetime.timedelta(days = 1)).isoformat()
    tuotteet = db.get_consumption_after(eilinen)
    text = "```\nEdellisen päivän kulutus:\n"
    for i in tuotteet:
        text += "{:_<18.18}{:2d} kpl\n".format(i[0].strip() + " ", i[1])

    bot.send_message(config.ADMIN_CHAT, text + "```", parse_mode="MARKDOWN")


def velo(bot, update):
    """Encourages people who are more than 5€ negative in their tab to pay their debts."""

    if is_admin(bot, update):
        velalliset = db.get_velalliset()
        for i in velalliset:
            bot.send_photo(i[0], open("velat.jpg", "rb"))

def komennot(bot, update):
    """Lists the commands usable by the regular user."""
    if is_registered(bot, update):
        bot.send_message(update.message.chat.id,
        """Komennot:
/piikki_ohje Ohje kaupan käyttöön.
/kauppa Osta asioita piikilläsi.
/hinnasto Tulosta tuotteiden hinnat.
/saldo Tarkista piikkisi arvo ja lisää ja poista rahaa.
/poista_edellinen Poista viimeisin tapahtuma.
""")

def commands(bot, update):
    """Lists the commands usable by an admin."""
    if is_admin(bot, update):
        bot.send_message(update.message.chat.id,
        """Komennot:
Viestittely:
/help
/tapahtumat
/tanaan
/kuva

Käyttäjät:
/kirjaudu
/piikki_ohje
/saldo
/poista_edellinen
/kauppa
/hinnasto

Admin:
/velo
/export_users
/export_transactions
/export_inventory
/import_inventory
""")


def is_registered(bot, update):
    """Check if user is registered."""
    user = update.effective_user
    if len(db.get_user(user.id)) < 1:
        bot.send_message(update.message.chat.id, "Rekisteröidy käyttääksesi tätä toiminnallisuutta kirjoittamalla /kirjaudu.")
        return False
    else:
        return True

def is_admin(bot, update):
    """Check if user is admin."""

    if update.effective_user.id in config.BOT_ADMINS:
        return True
    else:
        bot.send_message(update.message.chat.id, "You are not authorized.")
        return False

#ConversationHandler function that handles the conversation for deleting previous action.
poisto_handler = ConversationHandler(
    entry_points = [CommandHandler("poista_edellinen", poistatko, Filters.private)],
    states = {
        POISTA: [RegexHandler('^(Kyllä|Ei)$', poista)]
    },
    fallbacks = [CommandHandler("lopeta", lopeta), MessageHandler(Filters.all, tuntematon)],
    allow_reentry = True
)

#ConversationHandler function that handles the conversation for topping up or withdrawing money from account.
saldo_handler = ConversationHandler(
    entry_points = [CommandHandler("saldo", saldo, Filters.private)],
    states = {
        ALKU: [MessageHandler(Filters.text, saldo)],
        OHJAA: [RegexHandler('^({}|{}|{})$'.format(saldo_sanat[0], saldo_sanat[1], saldo_sanat[2]), ohjaa)],
        LISAA: [MessageHandler(Filters.text, lisaa)],
        NOSTA: [MessageHandler(Filters.text, nosta)],
    },
    fallbacks = [CommandHandler("lopeta", lopeta), MessageHandler(Filters.all, tuntematon)],
    allow_reentry = True

)

#Conversation handler function that handles the conversation for registering as an user.
register_handler = ConversationHandler(
    entry_points = [CommandHandler("kirjaudu", rekisteroidy, Filters.private)],
    states = {
        HYVAKSYN: [MessageHandler(Filters.all, hyvaksyn)]
    },
    fallbacks = [CommandHandler("lopeta", lopeta),  MessageHandler(Filters.all, tuntematon)]
)
