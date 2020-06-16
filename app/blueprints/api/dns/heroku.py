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

            # Create the DNS in CloudFlare
            from app.blueprints.api.dns.cloudflare import create_dns
            return create_dns(subdomain, dns)

        return False
    except Exception as e:
        print_traceback(e)
        return False