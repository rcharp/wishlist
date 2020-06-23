import os
import heroku3
from flask import current_app
from requests.exceptions import HTTPError


def create_subdomain(subdomain):
    from app.blueprints.base.functions import print_traceback

    try:
        heroku_conn = heroku3.from_key(os.environ.get('HEROKU_TOKEN'))
        app = heroku_conn.apps()['getwishlist']
        if app.get_domain(subdomain + '.getwishlist.io') is not None:
            return True

        d = app.add_domain(subdomain + '.getwishlist.io')
        print(d)

        if d is not None:
            print('DNS')
            dns = d.cname
            print(dns)

            # Create the DNS in CloudFlare
            from app.blueprints.base.dns.cloudflare import create_dns
            return create_dns(subdomain, dns)

        return False
    except HTTPError as h:
        if h.response.status_code == 422:
            heroku_conn = heroku3.from_key(os.environ.get('HEROKU_TOKEN'))
            app = heroku_conn.apps()['getwishlist']

            d = app.get_domain(subdomain + '.getwishlist.io')

            if d is not None:
                dns = d.cname

                # Create the DNS in CloudFlare
                from app.blueprints.base.dns.cloudflare import create_dns
                return create_dns(subdomain, dns)
            return False
    except Exception as e:
        print_traceback(e)
        return False