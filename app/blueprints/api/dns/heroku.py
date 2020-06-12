import heroku3


def create_subdomain(subdomain):
    heroku_conn = heroku3.from_key('HEROKU_API_KEY')

    app = heroku_conn.apps()['getwishlist']
    domain = app.add_domain(subdomain + '.getwishlist.io')