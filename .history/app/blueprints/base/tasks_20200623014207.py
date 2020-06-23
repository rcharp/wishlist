from app.app import create_celery_app, db
from flask import jsonify, make_response
from app.blueprints.user.models.domain import Domain
from app.blueprints.user.models.user import User
from app.blueprints.base.encryption import encrypt_string

celery = create_celery_app()


@celery.task()
def create_domain(user_id, email, domain, company):
    from app.blueprints.base.functions import generate_id, generate_private_key, print_traceback
    
    try:
        d = Domain()
        d.domain_id = generate_id(Domain, 8)
        d.name = domain
        d.company = company
        d.user_id = user_id
        d.admin_email = email
        d.private_key = encrypt_string(generate_private_key())
        d.save()

        u = User.query.filter(User.id == id).scalar()
        u.domain_id = d.domain_id
        u.domain = d.name
        u.save()

        if create_subdomain(domain):
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
