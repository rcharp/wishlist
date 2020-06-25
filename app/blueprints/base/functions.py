import string
import random
import pytz
import names
import traceback
from datetime import datetime as dt
from app.extensions import db
from sqlalchemy import exists, and_
from app.blueprints.base.encryption import encrypt_string
from app.blueprints.user.models.domain import Domain
from app.blueprints.base.models.feedback import Feedback
from app.blueprints.base.models.status import Status
from app.blueprints.base.models.vote import Vote


# Generations ###################################################
def generate_id(table, size=8):
    # Generate a random 8-digit id
    chars = string.digits
    id = int(''.join(random.choice(chars) for _ in range(size)))

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(table.id == id)).scalar():
        return id
    else:
        generate_id(table)


def generate_alphanumeric_id(table, size=8):
    # Generate a random 8-character alphanumeric id
    chars = string.digits + string.ascii_lowercase
    id = ''.join(random.choice(chars) for _ in range(size))

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(table.id == id)).scalar():
        return id
    else:
        generate_id(table)


def generate_temp_password(size=15):
    # Generate a random 15-character temporary password
    chars = string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def generate_private_key(size=16):
    from app.blueprints.base.encryption import encrypt_string

    # Generate a random 16-character alphanumeric id
    chars = string.digits + string.ascii_lowercase
    id = ''.join(random.choice(chars) for _ in range(size))

    # Encrypt the private key
    enc = encrypt_string(id)

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(Domain.private_key == enc)).scalar():
        return enc
    else:
        generate_private_key()


# Feedback ###################################################
def create_domain(user, domain, company):
    d = Domain()
    d.domain_id = generate_id(Domain, 8)
    d.name = domain
    d.company = company
    d.user_id = user.id
    d.admin_email = user.email
    d.save()

    user.domain_id = d.domain_id
    user.domain = domain
    user.save()

    return d.domain_id


# Feedback ###################################################
def create_feedback(user, domain, email, title, description):
    try:
        d = Domain.query.filter(Domain.name == domain).scalar()
        s = Status.query.filter(Status.name == 'In backlog').scalar()

        feedback_id = generate_id(Feedback, size=8)

        f = Feedback()
        f.title = title
        f.feedback_id = feedback_id
        f.description = description
        f.domain_id = d.domain_id
        f.domain = d.name
        f.status = s.name
        f.status_id = s.status_id

        if user is not None:
            f.user_id = user.id
            f.username = user.username
            f.fullname = user.name
            f.email = user.email

            add_vote(feedback_id, user)
        else:
            f.email = email
            user = create_anon_user(email)
            add_vote(feedback_id, user, email)

        f.save()

        return f
    except Exception as e:
        print_traceback(e)
        return None


def update_feedback(feedback_id, domain, title, description, status_id):
    try:
        s = Status.query.filter(Status.status_id == status_id).scalar()

        f = Feedback.query.filter(and_(Feedback.domain == domain, Feedback.feedback_id == feedback_id)).scalar()
        f.title = title
        f.description = description
        f.status = s.name
        f.status_id = s.status_id
        f.save()

        return f
    except Exception as e:
        print_traceback(e)
        return None


# Votes ###################################################
def add_vote(feedback_id, user, email=None):
    try:
        f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()

        v = Vote()
        v.feedback_id = feedback_id
        v.vote_id = generate_id(Vote)
        v.domain_id = f.domain_id

        if user is not None:
            v.user_id = user.id
        else:
            v.email = email

        v.save()

        f.votes += 1
        f.save()

        return v
    except Exception as e:
        print_traceback(e)
        return None


def remove_vote(feedback_id, vote):
    try:
        vote.delete()

        f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()
        f.votes -= 1
        f.save()
    except Exception as e:
        print_traceback(e)
        return None


# Users ###################################################
def create_anon_user(email):
    from app.blueprints.user.models.user import User
    if not db.session.query(exists().where(User.email == email)).scalar():
        password = generate_temp_password()
        u = User()
        u.email = email
        u.user_id = generate_id(User)
        u.role = 'member'
        u.password = User.encrypt_password(password)
        u.save()

        return u
    return None


def populate_signup(request, user):
    user.created_on = dt.now().replace(tzinfo=pytz.utc)
    user.updated_on = dt.now().replace(tzinfo=pytz.utc)
    user.role = request.form['role']
    user.is_active = True
    user.name = request.form['name']
    user.email = request.form['email']


def generate_name():
    return names.get_first_name()


def get_private_key(domain_id, user_id):

    d = Domain.query.filter(Domain.domain_id == domain_id).scalar()
    from app.blueprints.base.encryption import decrypt_string
    return decrypt_string(d.private_key)


# Other ###################################################
def print_traceback(e):
    traceback.print_tb(e.__traceback__)
    print(e)