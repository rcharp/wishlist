from app.blueprints.base.dns.heroku import create_subdomain


def test():
    return create_subdomain('test')