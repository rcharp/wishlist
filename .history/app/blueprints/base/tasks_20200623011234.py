from app.app import create_celery_app, db
from flask import jsonify, make_response
from app.blueprints.user.models.domain import Domain
from app.blueprints.base.encryption import encrypt_string
from app.blueprints.base.functions import generate_id, generate_private_key, print_traceback

celery = create_celery_app()


@celery.task()
def create_domain(user, form):
    try:
        d = Domain()
        d.domain_id = generate_id(Domain, 8)
        d.name = form.domain.data
        d.company = form.company.data
        d.user_id = user.id
        d.admin_email = user.email
        d.private_key = encrypt_string(generate_private_key())
        d.save()

        user.domain_id = d.domain_id
        user.domain = d.name
        user.save()

        if create_subdomain(form.domain.data):
            return True
        else:
            # d.delete()
            return False
    except Exception as e:
        print_traceback(e)
        return False


@celery.task()
def create_subdomain(subdomain):
    # Create the subdomain in Heroku
    from app.blueprints.base.dns.heroku import create_subdomain
    return create_subdomain(subdomain)
