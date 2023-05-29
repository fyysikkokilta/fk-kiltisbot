import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, datetime

from telegram import Update
from telegram.ext import CallbackContext

# TODO if user has no transaction history command crashes
# with 'DataFrame' object has no attribute 'tuote' caption text.
# TODO save images to img folder


def get_data():
    """Returns dataframe with all purchase data"""

    conn = sqlite3.connect("data/kiltis.db")
    sql = "SELECT * FROM transactions"
    data = pd.read_sql(sql, conn)
    return data[(data.tuote != "NOSTO") & (data.tuote != "PANO")]


def plot_histogram(data_user, uid):
    """Plots histogram of user's consumption data"""

    purchases_by_product = data_user.groupby("tuote").count().sort_values("id", ascending=True).reset_index()
    fig, ax = plt.subplots(1, figsize=(7, 8))
    ax.barh(purchases_by_product.tuote, purchases_by_product.id, 0.6, color="#201E1E")
    ax.tick_params(length=0)
    ax.xaxis.tick_top()
    ax.grid(color="white")
    ax.yaxis.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{uid}.png")


def past_two_weeks(ts):
    """
    Returns boolean whether string of form yyyy-mm-dd-something
    was during last two weeks
    """

    today = datetime.now()
    dt = timedelta(days=14)
    return datetime.strptime(ts[:10], "%Y-%m-%d") > today - dt


# TODO reverse order of products in caption.
def caption_text(data, data_user, uid):
    """Returns caption text that contains aggregate figures"""

    purchases = len(data_user)
    cost = data_user.hinta.sum() / 100
    # make sure there is data before doing calculations
    if purchases != 0:
        rank = list(data.user.value_counts().values).index(len(data_user)) + 1
        y, m, d = min(data_user.aika)[:10].split("-")
    else:
        rank = "NaN"
        y, m, d = "x", "x", "x"
    recent_purchases = [past_two_weeks(x) for x in data_user.aika.values]
    # hack to allow new line inside f string on last line
    return f""" Alkaen {d}.{m}.{y}
yhteensä {purchases} ostoa {cost:.2f} eurolla.
Olet piikin käytössä sijalla {rank}.

Viimeiset kaksi viikkoa:
{ chr(10).join(x for x in data_user[recent_purchases].tuote.values) }"""


async def send_histogram(update: Update, context: CallbackContext):
    """Sends histogram of consumption data to user with caption"""
    assert update.message is not None, "Update unexpectedly has no message"

    # TODO check is user is registered or data is empty of something like that
    uid = update.message.chat.id
    data = get_data()
    data_user = data[data.user == uid]
    caption = caption_text(data, data_user, uid)
    plot_histogram(data_user, uid)
    context.bot.send_photo(uid, open(f"{uid}.png", "rb"), caption=caption)
    os.remove(f"{uid}.png")
