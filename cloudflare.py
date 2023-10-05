import random
import subprocess
import ipaddress
import os
import requests

from dns_cf import main as cf_refresh

def ip_from_fetch():
    '''
    从 url 文件中读取 IP 段
    https://www.cloudflare.com/ips/
    '''
    ip_url = 'https://www.cloudflare.com/ips-v4'
    response = requests.get(ip_url)
    if response.status_code != 200:
        raise ValueError(f'status code {response.status_code}')
    ip_string = response.text
    ip_list = ip_string.strip().splitlines()
    return [ip.strip() for ip in ip_list if ip.strip()]

def ip_from_file():
    '''
    从 ip.txt 文件中读取 IP 段
    https://www.cloudflare.com/ips/
    '''
    ip_url = 'https://www.cloudflare.com/ips-v4'
    # 若不存在此 ip.txt 文件，则从网络上下载
    if not os.path.exists('ip.txt'):
        subprocess.call(['wget', '-O', 'ip.txt', ip_url])

    with open('ip.txt', 'r') as file:
        return file.read().splitlines()

def ip_from_string():
    '''
    IP 段作为 string
    '''
    ip_string = '''
    173.245.48.0/20
    103.21.244.0/22
    103.22.200.0/22
    103.31.4.0/22
    141.101.64.0/18
    108.162.192.0/18
    190.93.240.0/20
    188.114.96.0/20
    197.234.240.0/22
    198.41.128.0/17
    162.158.0.0/15
    104.16.0.0/12
    172.64.0.0/17
    172.64.128.0/18
    172.64.192.0/19
    172.64.224.0/22
    172.64.229.0/24
    172.64.230.0/23
    172.64.232.0/21
    172.64.240.0/21
    172.64.248.0/21
    172.65.0.0/16
    172.66.0.0/16
    172.67.0.0/16
    131.0.72.0/22
    '''
    # 将上述的 ip_str 转为 list
    ip_list = ip_string.strip().splitlines()
    return [ip.strip() for ip in ip_list if ip.strip()]

def run():
    try:
        # 存储所有测速结果的字典
        speed_results = []
        ip_ranges = ip_from_fetch()
        # ip_ranges = ip_from_file()
        # ip_ranges = ip_from_string()

        # 遍历每个 IP 段
        for ip_range in ip_ranges:
            # 解析 IP 段
            ip_network = ipaddress.IPv4Network(ip_range, strict=False)
            
            # 随机选择 3 个 IP 地址
            num_ips = min(3, ip_network.num_addresses - 2)  # 减去网络地址和广播地址
            ips = [str(ip) for ip in random.sample(list(ip_network.hosts()), num_ips)]
            
            # 测速并记录结果
            speeds = []
            for ip in ips:
                try:
                    result = subprocess.check_output(['ping', '-c', '3', '-W', '5', ip])
                    lines = result.decode('utf-8').splitlines()
                    for line in lines:
                        if 'avg' in line:
                            speed = float(line.split('/')[4])
                            speeds.append((ip, speed))
                except subprocess.CalledProcessError:
                    pass
            
            # 如果至少有一个 IP 测速成功，则记录最快的 IP 地址和速度
            if speeds:
                fastest_ip, fastest_speed = min(speeds, key=lambda x: x[1])
                speed_results.append((fastest_ip, fastest_speed))

        print(f'valid ip count: {len(speed_results)}')

        if len(speed_results) == 0:
            raise ValueError(f'No valid IP address')

        sorted_results = sorted(speed_results, key=lambda x: x[1])
        print(f'Fast CloudFlare IP: {sorted_results[0]}')

        best_ip = sorted_results[0][0]
        refresh(best_ip)
        # 若更新 cloudflare ns 成功，则返回该 IP
        return best_ip

    except Exception as e:
        print(f'Failed to get cloudflare best ip.  {e}')

def refresh(ip):
    '''
    更新 cloudflare 的 IP 到 cloudflare
    '''
    # 从环境变量中读取 CLOUDFLARE_DOMAIN, CLOUDFLARE_TOKEN
    domain = os.environ.get('CLOUDFLARE_DOMAIN')
    token = os.environ.get('CLOUDFLARE_TOKEN')
    if domain and token:
        cf_refresh(ip_address=ip, record_name=domain, token=token)