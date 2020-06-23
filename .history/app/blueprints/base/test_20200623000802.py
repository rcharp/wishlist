from app.blueprints.base.functions import print_traceback


def test():
    from app.blueprints.base.dns.heroku import create_subdomain

    try:
        return create_subdomain('test')
    except Exception as e:
        print_traceback(e)
        return None