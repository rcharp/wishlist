import heroku3
from flask import current_app


def create_subdomain(subdomain):
    from app.blueprints.api.api_functions import print_traceback
    try:
        heroku_conn = heroku3.from_key(current_app.config.get('HEROKU_TOKEN'))

        app = heroku_conn.apps()['getwishlist']
        d = app.add_domain(subdomain + '.getwishlist.io')

        if d is not None:
            dns = d.cname
            print(dns)

            # Create the DNS in cloudflare
            from app.blueprints.api.dns.cloudflare import create_dns
            create_dns(subdomain, dns)
        return True
    except Exception as e:
        print_traceback(e)
        return False