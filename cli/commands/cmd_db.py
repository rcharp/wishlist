import click
import random
from cli.commands.data import (
    statuses,
    titles,
    descriptions
)
from sqlalchemy_utils import database_exists, create_database
from app.app import create_app
from app.extensions import db
from app.blueprints.api.api_functions import generate_id
from app.blueprints.user.models.user import User
from app.blueprints.user.models.domain import Domain
from app.blueprints.billing.models.customer import Customer
from app.blueprints.api.models.status import Status
from app.blueprints.api.models.feedback import Feedback
from app.blueprints.api.models.vote import Vote
from app.blueprints.api.models.workspace import Workspace

# Create an app context for the database connection.
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()

    db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)


@click.command()
def seed_users():
    """
    Seed the database with an initial user.

    :return: User instance
    """
    if User.find_by_identity(app.config['SEED_ADMIN_EMAIL']) is not None:
        return None

    params = {
        'role': 'admin',
        'email': app.config['SEED_ADMIN_EMAIL'],
        'username': app.config['SEED_ADMIN_USERNAME'],
        'password': app.config['SEED_ADMIN_PASSWORD'],
        'name': 'Admin'
    }

    member = {
        'role': 'member',
        'email': app.config['SEED_MEMBER_EMAIL'],
        'username': app.config['SEED_MEMBER_USERNAME'],
        'password': app.config['SEED_ADMIN_PASSWORD'],
        'name': 'Ricky'
    }

    demo = {
        'role': 'creator',
        'email': 'demo@getwishlist.io',
        'username': 'demo',
        'password': app.config['SEED_ADMIN_PASSWORD'],
        'name': 'Demo User'
    }

    User(**member).save()
    User(**demo).save()

    return User(**params).save()


@click.command()
def seed_customers():
    params = {
        'user_id': 1,
        'customer_id': app.config['SEED_CUSTOMER_ID'],
        'email': app.config['SEED_MEMBER_EMAIL'],
        'save_card': True
    }

    return Customer(**params).save()


@click.command()
def seed_status():
    for status in statuses():
        params = {
            'status_id': generate_id(Status),
            'name': status['name'],
            'color': status['color']
        }

        Status(**params).save()

    return


@click.command()
def seed_domains():
    demo = {
        'domain_id': generate_id(Domain),
        'name': 'demo',
        'company': 'Demo',
        'admin_email': 'demo@getwishlist.io',
        'user_id': 2
    }

    Domain(**demo).save()


@click.command()
def seed_data():

    s = list(Status.query.all())
    d = Domain.query.filter(Domain.name == 'demo').scalar()

    for x in range(1, 31):
        status = random.choice(s)
        params = {
            'user_id': 2,
            'feedback_id': generate_id(Feedback),
            'title': random.choice(titles()),
            'email': 'demo@getwishlist.io',
            'username': "demo",
            'description': random.choice(descriptions()),
            'votes': random.randint(10, 1000),
            'status_id': status.status_id,
            'status': status.name,
            'domain': 'demo',
            'domain_id': d.domain_id
        }

        Feedback(**params).save()

    return


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.pass_context
def reset(ctx, with_testdb):
    """
    Init and seed_users automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed_users)
    ctx.invoke(seed_domains)
    ctx.invoke(seed_status)
    ctx.invoke(seed_data)

    return None


@click.command()
def backup():
    """
    Backup the db.
    :return: None
    """
    # from flask.alchemydumps import AlchemyDumps
    #
    # alchemydumps = AlchemyDumps(app, db)
    #
    # return alchemydumps.create()
    return None


cli.add_command(init)
cli.add_command(seed_users)
cli.add_command(reset)