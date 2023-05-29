"""
This file initializes database if it doesn't already exist and imports
database commands for conveniece.
"""

from os.path import isfile
from . import drive  # noqa: F401

from kiltisbot.db.commands import (
    initialize_db,
)

if not isfile("kiltis.db"):
    print("Creating new database.")
    initialize_db()
