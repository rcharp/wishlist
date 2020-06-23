import os
import heroku3
from flask import current_app
from requests.exceptions import HTTPError


def create_subdomain(subdomain):
    from app.blueprints.base.functions import print_traceback

    try:
        print("Heroku sub")
        print(subdomain)
        print(current_app.config.get('HEROKU_TOKEN'))

        heroku_conn = heroku3.from_key(current_app.config.get('HEROKU_TOKEN'))
        app = heroku_conn.apps()['getwishlist']

        try:
            d = app.get_domain(subdomain + '.getwishlist.io')
            if d is not None:
                try:
                    dns = d.cname
                    return create_dns(subdomain, dns)
                except Exception as e:
                    print_traceback(e)
                    pass
        except HTTPError as h:
            if h.response.status_code == 404:
                print(h)
                print("Domain doesn't exist.")
                pass

        try:
            d = app.add_domain(subdomain + '.getwishlist.io')
            print(d)
        except HTTPError as h:
            if h.response.status_code == 422:
                print(h)
                print("Domain already exists.")
                pass

        if d is not None:
            print('DNS')
            dns = d.cname
            print(dns)

            # Create the DNS in CloudFlare
            from app.blueprints.base.dns.cloudflare import create_dns
            return create_dns(subdomain, dns)

        return False
    except HTTPError as h:
        print(h.response.status_code)
        print(h)
        if h.response.status_code == 422:
            heroku_conn = heroku3.from_key(current_app.config.get('HEROKU_TOKEN'))
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