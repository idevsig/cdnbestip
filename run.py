import os
import gcore
import cloudflare
import notify

if __name__ == '__main__':
    if os.environ.get('CLOUDFLARE_TOKEN'):
        # 更新 gcore ip
        if os.environ.get('GCORE_DOMAIN'):
            ip = gcore.run()
            notify.Notify('Gcore Update', 'Gcore DNS IP: {}'.format(ip), 'daily').send()
        # 更新 cloudflare ip
        if os.environ.get('CLOUDFLARE_DOMAIN'):
            ip = cloudflare.run()
            notify.Notify('CloudFlare Update', 'CloudFlare DNS IP: {}'.format(ip), 'daily').send()
