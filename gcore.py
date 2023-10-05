import multiprocessing
import re
import requests
import subprocess
import platform
import sys
import os

from dns_cf import main as cf_refresh

def fetch():
    '''
    拉取数据并转为迭代器
    '''
    ip_url = 'https://api.gcore.com/cdn/public-ip-list'
    # ip_url = 'http://0.0.0.0:8000/gcore.json' # debug
    response = requests.get(ip_url)
    if response.status_code != 200:
        raise ValueError(f'status code {response.status_code}')
    resp = response.json()
    return [str(address).split('/')[0] for address in resp['addresses']]

def time_ms(match):
    '''
    将时间值转为毫秒
    :param value: 时间的值
    :param unit: 时间单位
    '''
    value = str(match[0]).strip()
    unit = str(match[1]).lower()
    if unit == "ms":
        return float(value)
    elif unit == "s":
        return float(value) * 1_000  # 将秒转换为毫秒
    elif unit == "us":
        return float(value) / 1_000 # 将微秒转换为毫秒
    return float(value) * 10_000_000

def check_ip(ip_address, result_queue):
    '''
    用于检查单个IP是否可达并获取响应时间
    :param ip_address: ip address
    :param result_queue: queue
    '''
    try:
        # 根据操作系统选择正确的 ping 命令
        if platform.system() == 'Windows':
            cmd = ['ping', ip_address, '-n', '1']
        else:  # Linux 和 macOS 使用不同的 ping 命令
            cmd = ['ping', ip_address, '-c', '1']

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)

        # print(f'result: {result.stdout}')
        if result.returncode == 0:
            rtt = -1  # 无法解析响应时间

            # 解析 ping 结果以获取响应时间（具体解析方法可能因操作系统而异）
            if platform.system() == 'Windows':
                rtt_line = [line for line in result.stdout.splitlines() if 'Average =' in line]
                if rtt_line:
                    rtt_str = rtt_line[0].split('=')[-1].strip()
                    rtt = float(rtt_str.split(' ')[0])
            else:  # Linux 和 macOS 的 ping 命令输出格式不同，您可能需要根据实际情况进行解析
                # 使用正则表达式匹配 "time=数字 单位" 格式的字符串
                # pattern = r"time=(\d+\s?\.\s?\d*)\s?(\w+)"
                pattern = r"time=(\d+\s?)\s?(\w+)"
                matches = re.findall(pattern, result.stdout)
                rtt = time_ms(matches[0])

            if rtt != -1:
                result_queue.put((ip_address, rtt))  # 将可达的IP地址和响应时间放入结果队列
    except Exception as e:
        # print(f'err {e}')
        pass  # 发生异常，忽略

def run():
    try:
        ip_list = fetch()
        print(f'ip count: {len(ip_list)}')
        # ip_list = ip_list[-1:]

        # 创建一个可在主进程和子进程之间共享的队列
        manager = multiprocessing.Manager()
        result_queue = manager.Queue()

        max_concurrency = 10  # 控制并发 ping 操作的数量
        pool = multiprocessing.Pool(max_concurrency)

        # 控制每次处理的 IP 地址的数量
        batch_size = 20  # 调整为适当的值
        for i in range(0, len(ip_list), batch_size):
            batch_ips = ip_list[i:i + batch_size]
            processes = []

            for ip in batch_ips:
                process = pool.apply_async(check_ip, args=(ip, result_queue))
                processes.append(process)

            for process in processes:
                process.get()  # 等待子进程完成

        pool.close()
        pool.join()

        valid_ips = []
        while not result_queue.empty():
            valid_ips.append(result_queue.get())
        print(f'valid ip count: {len(valid_ips)}')

        if len(valid_ips) == 0:
            raise ValueError(f'No valid IP address')

        valid_ips.sort(key=lambda x: x[1])  # 按响应时间从小到大排序
        # print(f'有效IP地址列表（按响应时间排序）:')
        # for ip, rtt in valid_ips:
        #     print(f'{ip} - 响应时间: {rtt}ms')
        
        print(f'Fast Gcore IP: {valid_ips[0]}')

        best_ip = valid_ips[0][0]
        refresh(best_ip)
        # 若更新 cloudflare ns 成功，则返回该 IP
        return best_ip

    except Exception as e:
        print(f'Failed to get gcore best ip.  {e}')

def refresh(ip):
    '''
    更新 gcore 的 IP 到 cloudflare
    '''
    # 从环境变量中读取 GCORE_DOMAIN, CLOUDFLARE_TOKEN
    domain = os.environ.get('GCORE_DOMAIN')
    token = os.environ.get('CLOUDFLARE_TOKEN')
    if domain and token:
        cf_refresh(ip_address=ip, record_name=domain, token=token)

def run_fast():
    '''
    多线程处理，未使用
    但是报错：[Errno 24] Too many open files
    '''
    try:
        ip_list = fetch()
        print(f'ip count {len(ip_list)}')
        # ip_list = ip_list[-10:]
        
        result_queue = multiprocessing.Queue()
        processes = []

        for ip in ip_list:
            process = multiprocessing.Process(target=check_ip, args=(ip, result_queue))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        valid_ips = []
        while not result_queue.empty():
            valid_ips.append(result_queue.get())
        print(f'valid ip count: {len(valid_ips)}')

        valid_ips.sort(key=lambda x: x[1])  # 按响应时间从小到大排序
        # print(f'有效IP地址列表（按响应时间排序）:')
        # for ip, rtt in valid_ips:
        #     print(f'{ip} - 响应时间: {rtt}ms')
        cf_refresh(valid_ips[0][0])

    except Exception as e:
        print(f'Failed to fetch gcore ip list.  {e}')
