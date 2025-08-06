import requests
from telegram import Update
from telegram.ext import ContextTypes

from kiltisbot import config


def get_newsletter_data(lang):
    url = f"{config.NEWSLETTER_BASE_URL}/api/newsletter/telegram?locale={lang}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data["newsletter"] is not None:
            return data["message"]
        else:
            return "Viikkotiedote on tyhjä" if lang == "fi" else "Weekly news is empty"
    elif response.status_code == 404:
        return "Viikkotiedotetta ei löytynyt" if lang == "fi" else "Weekly news not found"
    else:
        return "Virhe viikkotiedotetta haettaessa" if lang == "fi" else "Error fetching weekly news"


async def viikkotiedote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_newsletter_data("fi")
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text(message, parse_mode="HTML")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_newsletter_data("en")
    assert update.message is not None, "Update unexpectedly has no message"
    await update.message.reply_text(message, parse_mode="HTML")
