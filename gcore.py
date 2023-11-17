import requests
import os
from check import Check

from dns_cf import main as cf_refresh

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def fetch(cdn=''):
    '''
    拉取数据并转为迭代器
    '''
    cdn = '' if not cdn else cdn.rstrip('/') + '/'
    ip_url = '{}https://api.gcore.com/cdn/public-ip-list'.format(cdn)
    print(ip_url)
    response = requests.get(ip_url, timeout=5)
    if response.status_code != 200:
        raise ValueError(f'status code {response.status_code}')
    resp = response.json()
    return [str(address).split('/')[0] for address in resp['addresses']]


def run():
    try:
        # 从环境变量中读取 GCORE_DOMAIN, CLOUDFLARE_TOKEN
        source_cdn = os.environ.get('SOURCE_CDN', '')
        token = os.environ.get('CLOUDFLARE_TOKEN')
        skip = os.environ.get('GCORE_VALID_SKIP')
        domain = os.environ.get('GCORE_DOMAIN')
        check_domain = os.environ.get('GCORE_CHECK_DOMAIN', 'gcore.com')

        check = Check(check_domain)

        # 源IP有效开关
        if skip:
            old_ip = check.domain_ip(domain)
            # 源IP有效则返回
            if old_ip:
                return old_ip

        ip_list = fetch(source_cdn)
        print(f'ip count: {len(ip_list)}')
        # ip_list = ip_list[-1:]
        # print(ip_list)

        valid_ips = check.run(ip_list)
        print(f'valid ip count: {len(valid_ips)}')

        if len(valid_ips) == 0:
            raise ValueError(f'No valid IP address')

        # 按响应时间从小到大排序
        valid_ips.sort(key=lambda x: x[1])
        # print(f'有效IP地址列表（按响应时间排序）:')
        # for ip, rtt in valid_ips:
        #     print(f'{ip} - 响应时间: {rtt}ms')

        print(f'Fast Gcore IP: {valid_ips[0]}')

        best_ip = valid_ips[0][0]

        # 更新 CF IP
        refresh(best_ip, domain, token)

        # 若更新 cloudflare ns 成功，则返回该 IP
        return best_ip

    except Exception as e:
        print(f'Failed to get gcore best ip.  {e}')


def refresh(ip, domain, token):
    '''
    更新 gcore 的 IP 到 cloudflare
    '''
    if domain and token:
        cf_refresh(ip_address=ip, record_name=domain, token=token)
