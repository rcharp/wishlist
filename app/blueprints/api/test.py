from app.blueprints.api.dns.heroku import create_subdomain


def test():
    return create_subdomain('test')