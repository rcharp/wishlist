import CloudFlare
import os
from flask import current_app


def create_dns(subdomain, dns):
    from app.blueprints.base.functions import print_traceback
    zone_name = 'getwishlist.io'
    cf = CloudFlare.CloudFlare(token=current_app.config.get('CLOUDFLARE_TOKEN'))

    # query for the zone name and expect only one value back
    try:
        zones = cf.zones.get(params={'name': zone_name, 'per_page': 1})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        print_traceback(e)
        return False
        # exit('/zones.get %d %s - base call failed' % (e, e))
    except Exception as e:
        print_traceback(e)
        return False
        # exit('/zones.get - %s - base call failed' % (e))

    if len(zones) == 0:
        return False

    # extract the zone_id which is needed to process that zone
    zone = zones[0]
    zone_id = zone['id']

    # request the DNS records from that zone
    try:
        dns_records = cf.zones.dns_records.get(zone_id)
        for r in dns_records:
            r_name = r['name']
            print(r_name)
        
        record = {'name': subdomain, 'type':'CNAME', 'content': dns, 'proxied': True}
        r = cf.zones.dns_records.post(zone_id, data=record)
        return True
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        print_traceback(e)
        return False
        # exit('/zones/dns_records.get %d %s - base call failed' % (e, e))
