import heroku3
from flask import current_app


def create_subdomain(subdomain):
    from app.blueprints.api.api_functions import print_traceback
    try:
        heroku_conn = heroku3.from_key(current_app.config.get('HEROKU_TOKEN'))

        app = heroku_conn.apps()['getwishlist']
        domain = app.add_domain(subdomain + '.getwishlist.io')

    #     -d
    #     '{
    #     "hostname": "subdomain.example.com"
    # }' \
    #       -H "Content-Type: application/json" \
    #       -H "Accept: application/vnd.heroku+json; version=3"
    # Authorization: Bearer
    # 01234567 - 89
    # ab - cdef - 0123 - 456789
    # abcdef
    #
    # headers = {
    # "Authorization": "Bearer " + token,
    # "Content-Type": "application/json"
    #
    # }
    #
    # r = requests.get(url, headers=headers)
        return True
    except Exception as e:
        print_traceback(e)
        return False