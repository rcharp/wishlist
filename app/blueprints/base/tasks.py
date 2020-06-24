from app.app import create_celery_app
from app.blueprints.user.models.domain import Domain
from app.blueprints.user.models.user import User

celery = create_celery_app()


@celery.task()
def populate_domain(domain_id):
    from app.blueprints.base.functions import generate_id, generate_private_key, print_traceback
    # from app.blueprints.base.encryption import encrypt_string

    try:
        d = Domain.query.filter(Domain.domain_id == domain_id).scalar()
        d.private_key = encrypt_string.delay(generate_private_key())
        d.save()

        return True
    except Exception as e:
        print_traceback(e)
        return False


@celery.task()
def create_heroku_subdomain(subdomain):
    # Create the subdomain in Heroku
    from app.blueprints.base.dns.heroku import create_subdomain
    return create_subdomain(subdomain)


@celery.task()
def encrypt_string(plaintext):
    from app.blueprints.base.encryption import encrypt_string
    return encrypt_string(plaintext)
