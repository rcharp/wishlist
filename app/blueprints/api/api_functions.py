import string
import random
import traceback
from app.extensions import db
from sqlalchemy import exists
from app.blueprints.api.models.workspace import Workspace
from app.blueprints.api.models.feedback import Feedback
from app.blueprints.api.models.vote import Vote


def generate_id(table, size=8):
    # Generate a random 7-character record id
    chars = string.digits
    id = int(''.join(random.choice(chars) for _ in range(size)))

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(table.id == id)).scalar():
        return id
    else:
        generate_id(table)


def generate_alphanumeric_id(table, size=8):
    # Generate a random 7-character record id
    chars = string.digits + string.ascii_lowercase
    id = ''.join(random.choice(chars) for _ in range(size))

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(table.id == id)).scalar():
        return id
    else:
        generate_id(table)


def create_workspace(user_id, title, domain, description):
    try:
        id = generate_id(Workspace, size=8)
        w = Workspace()
        w.admin_id = user_id
        w.title = title
        w.workspace_id = id
        w.domain = domain
        w.description = description
        w.save()

        return w
    except Exception as e:
        print_traceback(e)
        return None


def create_feedback(user_id, email, title, description):
    try:
        id = generate_id(Feedback, size=8)
        f = Feedback()
        f.user_id = user_id
        f.email = email
        f.title = title
        f.feedback_id = id
        f.description = description
        f.save()

        return f
    except Exception as e:
        print_traceback(e)
        return None


def add_vote(feedback_id, user_id):
    try:
        v = Vote()
        v.feedback_id = feedback_id
        v.vote_id = generate_id(Vote)
        v.user_id = user_id
        v.voted = True
        v.save()

        f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()
        f.votes += 1
        f.save()

        return v
    except Exception as e:
        print_traceback(e)
        return None


def print_traceback(e):
    traceback.print_tb(e.__traceback__)
    print(e)
