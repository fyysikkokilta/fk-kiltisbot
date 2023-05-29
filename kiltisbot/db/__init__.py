# noqa: F401
"""
This file initializes database if it doesn't already exist and imports
database commands for conveniece.
"""

from os.path import isfile
from . import drive

from kiltisbot.db.commands import (
    add_user,
    add_transaction,
    add_item,
    update_balance,
    delete_inventory,
    delete_users,
    delete_transactions,
    get_user,
    get_users,
    get_velalliset,
    get_balance,
    get_price,
    get_items,
    get_stocks,
    get_last_transaction,
    get_transactions_after,
    get_consumption_after,
    delete_transaction,
    update_stock,
    set_stock_0,
    print_users,
    print_inventory,
    print_transactions,
    initialize_db,
)

if not isfile("kiltis.db"):
    print("Creating new database.")
    initialize_db()

__all__ = [
    "add_user",
    "add_transaction",
    "add_item",
    "update_balance",
    "delete_inventory",
    "delete_users",
    "delete_transactions",
    "get_user",
    "get_users",
    "get_velalliset",
    "get_balance",
    "get_price",
    "get_items",
    "get_stocks",
    "get_last_transaction",
    "get_transactions_after",
    "get_consumption_after",
    "delete_transaction",
    "update_stock",
    "set_stock_0",
    "print_users",
    "print_inventory",
    "print_transactions",
    "initialize_db",
    "drive",
]
