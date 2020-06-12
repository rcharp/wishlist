import heroku3


def create_subdomain(subdomain):
    from app.blueprints.api.api_functions import print_traceback
    try:
        heroku_conn = heroku3.from_key('HEROKU_TOKEN')

        app = heroku_conn.apps()['getwishlist']
        domain = app.add_domain(subdomain + '.getwishlist.io')

        return True
    except Exception as e:
        print_traceback(e)
        return False