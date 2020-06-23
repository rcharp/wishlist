def test():
    from app.blueprints.base.dns.heroku import create_subdomain
    return create_subdomain('test')