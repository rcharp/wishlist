import string
import random
import traceback
from app.extensions import db
from sqlalchemy import exists


def generate_id(table, size=8):
    # Generate a random 7-character record id
    chars = string.digits
    id = int(''.join(random.choice(chars) for _ in range(size)))

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(table.id == id)).scalar():
        return id
    else:
        generate_id(table)


def print_traceback(e):
    traceback.print_tb(e.__traceback__)
    print(e)
