#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import os
import gcore
import cloudflare
from notify import send

"""
File: run.py(最优CDN域名IP更新)
Author: Jetsung
cron: 0 7 * * *
new Env('最优CDN域名IP更新');
Update: 2023/10/21
"""

if __name__ == '__main__':
    if os.environ.get('CLOUDFLARE_TOKEN'):
        # 更新 gcore ip
        if os.environ.get('GCORE_DOMAIN'):
            ip = gcore.run()
            send('Gcore Update', f'Gcore DNS IP: {ip}')

        # 更新 cloudflare ip
        if os.environ.get('CLOUDFLARE_DOMAIN'):
            ip = cloudflare.run()
            send('CloudFlare Update', f'CloudFlare DNS IP: {ip}')
