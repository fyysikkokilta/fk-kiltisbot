"""Wrapper for sqlite3 library for this application. Consist of two wrappers
and functions that take cursor to db as first argument."""

import sqlite3
from typing import Callable, Concatenate, ParamSpec, TypeVar

# TODO consider removing määrä from item database fields
# as it is not used and also update_stock and set_stock_0, get_stocks

Param = ParamSpec("Param")
RetType = TypeVar("RetType")
OrigFun = Callable[Concatenate[sqlite3.Cursor, Param], RetType]
DecFun = Callable[Param, RetType]


def commit(func: OrigFun) -> DecFun:
    """Decorator that opens and closes database connection for actions that
    change something in database. Passes cursor to function as first argument."""

    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("kiltis.db")
        cursor = conn.cursor()
        func(cursor, *args, **kwargs)
        conn.commit()
        conn.close()

    return wrapper


def get(func: OrigFun) -> DecFun:
    """Decorator that opens and closes database connection for actions that
    read data from database and returns whatever function returns.
    Passes cursor to function as first argument."""

    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("kiltis.db")
        cursor = conn.cursor()
        out = func(cursor, *args, **kwargs)
        conn.close()
        return out

    return wrapper


@commit
def initialize_db(c):
    c.execute("CREATE TABLE users (id int, nick text, nimi text, saldo int)")
    c.execute("CREATE TABLE inventory (nimi text, hinta int, maara int)")
    c.execute(
        "CREATE TABLE transactions (id integer primary key, user int, user_name text,"
        " tuote text, hinta int, aika text)"
    )


@commit
def add_user(c: sqlite3.Cursor, id, nick, nimi, saldo):
    c.execute("INSERT INTO users VALUES (?,?,?,?)", (id, nick, nimi, saldo))


@commit
def add_transaction(c, user, name, tuote, aika, hinta):
    c.execute(
        ("INSERT INTO transactions (id, user, user_name, tuote, hinta, aika) VALUES" " (NULL,?,?,?,?,?)"),
        (user, None, tuote, hinta, aika),
    )


@commit
def add_item(c, nimi, hinta, maara):
    c.execute("INSERT INTO inventory VALUES (?,?,?)", (nimi, hinta, maara))


@commit
def update_balance(c, user, delta):
    saldo = c.execute("SELECT saldo FROM users WHERE id = ?", (user,)).fetchone()[0]
    c.execute("UPDATE users SET saldo = ? WHERE id = ?", (saldo + delta, user))


@commit
def delete_inventory(c):
    c.execute("DELETE FROM inventory")


@commit
def delete_users(c):
    c.execute("DELETE FROM users")


@commit
def delete_transactions(c):
    c.execute("DELETE FROM transactions")


@commit
def delete_transaction(c, id):
    c.execute("DELETE FROM transactions WHERE id = ?", (id,))


@commit
def update_stock(c, nimi, delta):
    cur = c.execute("SELECT maara FROM inventory WHERE nimi=?", (nimi,)).fetchone()[0]
    c.execute("UPDATE inventory SET maara = ? WHERE nimi = ?", (cur + delta, nimi))


@commit
def set_stock_0(c, nimi):
    c.execute("UPDATE inventory SET maara = ? WHERE nimi = ?", (0, nimi))


@get
def get_user(c, id):
    return c.execute("SELECT * from users WHERE id=?", (id,)).fetchall()


@get
def get_users(c):
    return c.execute("SELECT * from users").fetchall()


@get
def get_velalliset(c):
    return c.execute("SELECT * from users WHERE saldo < -500").fetchall()


@get
def get_balance(c, id):
    return c.execute("SELECT saldo FROM users WHERE id=?", (id,)).fetchall()[0][0]


@get
def get_price(c, nimi):
    return c.execute("SELECT hinta FROM inventory WHERE nimi=?", (nimi,)).fetchall()[0][0]


# TODO consider changing this WHERE clause if maara is removed
@get
def get_items(c):
    return c.execute("SELECT * FROM inventory").fetchall()


@get
def get_stocks(c):
    return c.execute("SELECT maara FROM inventory").fetchall()


@get
def get_last_transaction(c, user):
    return c.execute("SELECT * FROM transactions WHERE user = ? ORDER BY aika DESC", (user,)).fetchall()[0]


@get
def get_transactions_after(c, time):
    return c.execute("SELECT * FROM transactions WHERE aika > ? ", (time,)).fetchall()


@get
def get_consumption_after(c, time):
    return c.execute(
        (
            "SELECT tuote, COUNT(tuote) FROM transactions WHERE aika > ? AND NOT"
            " tuote='PANO' AND NOT tuote='NOSTO' GROUP BY tuote"
        ),
        (time,),
    ).fetchall()


@get
def print_users(c):
    for row in c.execute("SELECT * FROM users"):
        print(row)


@get
def print_inventory(c):
    for row in c.execute("SELECT * FROM inventory"):
        print(row)


@get
def print_transactions(c):
    for row in c.execute("SELECT * FROM transactions"):
        print(row)
