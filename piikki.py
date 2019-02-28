
ALKU, LISAA, NOSTA, OHJAA, POISTA = range(5)
saldo_sanat = ["Näytä saldo 💶👀", "Lisää saldoa 💶⬆️", "Nosta rahaa saldosta 💶⬇️"]

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
 InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult)

from telegram.ext import (Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler,
  Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler)

import datetime
import db
import math
import drive

admin_ids = [51141559]

def store(bot, update):
    if not is_registered(bot, update):
        return

    products = db.get_items()
    print(products)

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

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Mitä laitetaan?', reply_markup=reply_markup)

def button(bot, update):
    if not is_registered(bot, update):
        return

    query = update.callback_query
    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()
    price = db.get_price(query.data)
    name = db.get_user(user)[0][2]
    print(price)

    db.add_transaction(user, name, query.data, time, price)
    db.update_stock(query.data, -1)
    db.update_balance(user, -price)

    saldo = db.get_balance(user)
    print(saldo)
    query.edit_message_text(text="Ostit tuotteen: {}.\n\nSaldoa jäljellä {:.2f}€".format(query.data, saldo / 100))

def rekisteroidy(bot, update):
    user = update.effective_user
    if len(db.get_user(user.id)) == 0:
        name = ""
        if user.first_name and user.last_name:
            name = "{} {}".format(user.first_name, user.last_name)
        else:
            name = user.first_name

        nick = ""
        if user.username:
            nick = user.username

        db.add_user(user.id, nick, name, 0)

        bot.send_message(update.effective_chat.id, "Onneksi olkoon! Sinut on nyt lisätty käyttäjäksi.")
    else:
        bot.send_message(update.effective_chat.id, "Olet jo käyttäjä.")

def saldo(bot, update):
    if not is_registered(bot, update):
        return

    global saldo_sanat
    keyboard = [[saldo_sanat[0]], [saldo_sanat[1]], [saldo_sanat[2]]]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)

    update.message.reply_text('Mitä haluaisit tehdä? Kirjoita missä vaiheessa tahansa /lopeta keskeyttäksesi toiminnon.', reply_markup=reply_markup)

    return OHJAA

def ohjaa(bot, update):
    global saldo_sanat
    print(update.effective_message.text)
    if update.effective_message.text == saldo_sanat[0]:
        saldo = db.get_balance(update.effective_user.id)
        bot.send_message(update.effective_chat.id, "Saldosi on {:.2f}€.".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    elif update.effective_message.text == saldo_sanat[1]:
        update.message.reply_text("Paljonko saldoa haluaisit lisätä?", reply_markup = ReplyKeyboardRemove())
        return LISAA

    elif update.effective_message.text == saldo_sanat[2]:
        update.message.reply_text("Paljonko rahaa haluaisit nostaa saldosta?", reply_markup = ReplyKeyboardRemove())
        return NOSTA
    else:
        return ConversationHandler.END

def lisaa(bot, update):
    maara = 0
    try:
        maara = int(float(update.message.text.replace(",", ".")) * 100)
    except ValueError:
        bot.send_message(update.message.chat.id, "Antamasi luku ei kelpaa. Lisääminen keskeytetty.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()

    db.update_balance(update.effective_user.id, maara)
    db.add_transaction(user, "PANO", time, maara)

    saldo = db.get_balance(update.effective_user.id)
    bot.send_message(update.message.chat.id, "Saldon lisääminen onnistui. Saldosi on nyt {:.2f}€".format(saldo / 100), reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END

def nosta(bot, update):
    maara = 0
    try:
        maara = int(float(update.message.text.replace(",", ".")) * 100)
    except ValueError:
        bot.send_message(update.message.chat.id, "Antamasi luku ei kelpaa. Nosto keskeytetty.", reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    user = update.effective_user.id
    time = datetime.datetime.today().isoformat()

    db.update_balance(update.effective_user.id, -maara)
    db.add_transaction(user, "NOSTO", time, maara)

    saldo = db.get_balance(update.effective_user.id)
    bot.send_message(update.message.chat.id, "Rahan nostaminen saldosta onnistui. Saldosi on nyt {:.2f}€".format(saldo / 100), reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END

def lopeta(bot, update):
    update.message.reply_text('Toiminto keskeytetty.', reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

def poistatko(bot, update):
    if not is_registered(bot, update):
        return

    keyboard = [["Kyllä", "Ei"]]
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
    if update.message.text == "Kyllä":
        user = update.effective_user.id
        edellinen = db.get_last_transaction(update.effective_user.id)
        print(edellinen[0])

        summa = -edellinen[4] if edellinen[3] == "PANO" else edellinen[4]

        if edellinen[3] != "PANO" and edellinen[3] != "NOSTO":
            db.update_stock(edellinen[3], 1)

        db.update_balance(user, summa)
        db.delete_transaction(edellinen[0])
        saldo = db.get_balance(user)

        bot.send_message(update.message.chat.id, "Tapahtuma poistettu. Tilisi saldo on {:.2f}€.".format(saldo / 100), reply_markup = ReplyKeyboardRemove())
    else:
        bot.send_message(update.message.chat.id, "Tapahtumaa ei poistettu", reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END

def hinnasto(bot, update):
    items = db.get_items()
    text = "```\nHinnasto:\n"
    for i in items:
        text += "{:18} {:.2f}€\n".format(i[0], i[1] /100)
    bot.send_message(update.message.chat.id, text + "```", parse_mode="MARKDOWN")


def export_users(bot, update):
    if is_admin(bot, update):
        drive.export_users()
        bot.send_message(update.message.chat.id, "Käyttäjien vieminen onnistui!")


def export_transactions(bot, update):
    if is_admin(bot, update):
        drive.export_transactions()
        bot.send_message(update.message.chat.id, "Tapahtumien vieminen onnistui!")


def export_inventory(bot, update):
    if is_admin(bot, update):
        drive.export_inventory()
        bot.send_message(update.message.chat.id, "Tuotteiden vieminen onnistui!")


def import_inventory(bot, update):
    if is_admin(bot, update):
        drive.import_inventory()
        bot.send_message(update.message.chat.id, "Tuotteiden tuominen onnistui!")

def commands(bot, update):
    if is_admin(bot, update):
        bot.send_message(update.message.chat.id,
        """Komennot:
/help
/saldo
/poista_edellinen
/kuva
/tapahtumat
/tanaan
/store
/rekisteroidy
/export_users
/export_transactions
/export_inventory
/import_inventory
/hinnasto""")


def is_registered(bot, update):
    user = update.effective_user
    if len(db.get_user(user.id)) == 0:
        bot.send_message(update.message.chat.id, "Rekisteröidy käyttääksesi tätä toiminnallisuutta kirjoittamalla /rekisteroidy.")
        return False
    else:
        return True

def is_admin(bot, update):
    if update.effective_user.id in admin_ids:
        return True
    else:
        bot.send_message(update.message.chat.id, "You are not authorized.")
        return False
