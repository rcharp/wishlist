import heroku3
from flask import current_app
from requests.exceptions import HTTPError


def create_subdomain(subdomain):
    from app.blueprints.base.functions import print_traceback

    heroku_conn = heroku3.from_key(current_app.config.get('HEROKU_TOKEN'))
    app = heroku_conn.apps()['getwishlist']
    try:
        d = app.add_domain(subdomain + '.getwishlist.io')

        if d is not None:
            dns = d.cname

            # Create the DNS in CloudFlare
            from app.blueprints.base.dns.cloudflare import create_dns
            return create_dns(subdomain, dns)

        return False
    except HTTPError as h:
        print(h.response)
        if 'Domain already added' in h.response:
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