import string
import random
import pytz
import names
import traceback
from datetime import datetime as dt
from app.extensions import db
from sqlalchemy import exists, and_
from app.blueprints.user.models.domain import Domain
from app.blueprints.api.models.workspace import Workspace
from app.blueprints.api.models.feedback import Feedback
from app.blueprints.api.models.status import Status
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


def create_feedback(user, domain, title, description):
    try:
        d = Domain.query.filter(Domain.name == domain).scalar()
        s = Status.query.filter(Status.name == 'In backlog').scalar()

        feedback_id = generate_id(Feedback, size=8)
        f = Feedback()
        f.user_id = user.id
        f.username = user.username
        f.fullname = user.name
        f.email = user.email
        f.title = title
        f.feedback_id = feedback_id
        f.description = description
        f.domain_id = d.domain_id
        f.domain = d.name
        f.status = s.name
        f.status_id = s.status_id
        f.save()

        add_vote(feedback_id, user.id)

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


def add_vote(feedback_id, user_id):
    try:
        f = Feedback.query.filter(Feedback.feedback_id == feedback_id).scalar()

        v = Vote()
        v.feedback_id = feedback_id
        v.vote_id = generate_id(Vote)
        v.user_id = user_id
        v.domain_id = f.domain_id
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


def print_traceback(e):
    traceback.print_tb(e.__traceback__)
    print(e)


def create_domain(user, form):
    try:
        d = Domain()
        d.domain_id = generate_id(Domain)
        d.name = form.domain.data
        d.company = form.company.data
        d.user_id = user.id
        d.admin_email = user.email
        d.save()

        if create_subdomain(form.domain.data):
            return True
        else:
            d.delete()
            return False
    except Exception as e:
        print_traceback(e)
        return False


def create_subdomain(subdomain):
    # Create the subdomain in Heroku
    from app.blueprints.api.dns.heroku import create_subdomain
    return create_subdomain(subdomain)


def populate_signup(request, user):
    user.created_on = dt.now().replace(tzinfo=pytz.utc)
    user.updated_on = dt.now().replace(tzinfo=pytz.utc)
    user.role = request.form['role']
    user.is_active = True
    user.name = request.form['name']
    user.email = request.form['email']


def generate_name():
    return names.get_full_name()