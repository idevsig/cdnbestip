import multiprocessing
import platform
import re
import subprocess
import requests


class Check:
    def __init__(self, domain, scheme='https') -> None:
        self.domain = domain
        self.scheme = 'http' if scheme == 'http' else 'https'

    def curl(self, ip_address, timeout=5):
        """
        判断是否可以访问指定的网址
        Check if a website is accessible by sending a HEAD request to the specified IP address.

        Parameters:
            ip_address (str): The IP address of the website.
            timeout (int, optional): The timeout for the request in seconds. Defaults to 5.

        Returns:
            bool: True if the website is accessible, False otherwise.
        """

        try:
            url = "{}://{}".format(self.scheme, ip_address)
            headers = {"Host": self.domain}    
            # print(url)        
            response = requests.head(url, headers=headers, allow_redirects=True, verify=False, timeout=timeout)
            if response.status_code == 200:
                # print("网站可访问！")
                return True
            # else:
                # print(f"无法访问，状态码: {response.status_code}")

        except requests.RequestException as e:
            # print(f"发生错误: {e}")
            pass
        return False

    def dig(self, domain):
        """
        根据域名通过 dig 命令获取正确的 IP
        Executes a ping or nslookup command based on the operating system to retrieve information about a domain.

        Args:
            domain (str): The domain to perform the command on.

        Returns:
            CompletedProcess: An object representing the completed process including the command's exit code, output, and error.

        Raises:
            subprocess.CalledProcessError: If the command fails or times out.

        Example:
            >>> dig('example.com')
            CompletedProcess(args=['nslookup', 'example.com'], returncode=0, stdout=b'...', stderr=b'...')
        """

        # 根据操作系统选择正确的 ping 命令
        if platform.system() == 'Windows':
            cmd = ['nslookup', domain]
        else:  # Linux 和 macOS 使用不同的 ping 命令
            cmd = ['dig', domain]

        resp = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=5)
        # print(resp)
        return resp

    def ping(self, ip_address):
        # 根据操作系统选择正确的 ping 命令
        if platform.system() == 'Windows':
            cmd = ['ping', ip_address, '-n', '1']
        else:  # Linux 和 macOS 使用不同的 ping 命令
            cmd = ['ping', ip_address, '-c', '1']

        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=5)

    def check_ip(self, ip_address, result_queue):
        """
        Check the reachability of an IP address and put the result into the result queue.
        检查单个IP是否可达并获取响应时间

        Parameters:
            ip_address (str): The IP address to check.
            result_queue (Queue): The queue to store the result.

        Returns:
            None
        """
        try:
            result = self.ping(ip_address)
            # print(f'result: {result.stdout}')
            if result.returncode == 0:
                rtt = -1  # 无法解析响应时间

                if not self.curl(ip_address, timeout=3):
                    return False
            
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
                    rtt = self.time2ms(matches[0])

                if rtt != -1:
                    result_queue.put((ip_address, rtt))  # 将可达的IP地址和响应时间放入结果队列
        except Exception as e:
            # print(f'err {e}')
            pass  # 发生异常，忽略

    def time2ms(self, match):
        """
        Convert a time value to milliseconds.
        转换时间值为毫秒

        Args:
            match (list): A list containing the time value and unit.

        Returns:
            float: The time value converted to milliseconds.

        Raises:
            None.
        """
        value = str(match[0]).strip()
        unit = str(match[1]).lower()
        if unit == "ms":
            return float(value)
        elif unit == "s":
            return float(value) * 1_000  # 将秒转换为毫秒
        elif unit == "us":
            return float(value) / 1_000  # 将微秒转换为毫秒
        return float(value) * 10_000_000

    def run(self, ip_list):
        """
        Run the IP list through a multiprocessing pool to check the validity of each IP address.

        Args:
            ip_list (List[str]): A list of IP addresses to be checked.

        Returns:
            List[str]: A list of valid IP addresses.
        """

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
                process = pool.apply_async(self.check_ip, args=(ip, result_queue))
                processes.append(process)

            for process in processes:
                process.get()  # 等待子进程完成

        pool.close()
        pool.join()

        valid_ips = []
        while not result_queue.empty():
            valid_ips.append(result_queue.get())
        return valid_ips

    def domain_ip(self, domain):
        """
        Get the IP address of a given domain.
        获取指定域名的IP

        Args:
            domain (str): The domain for which to retrieve the IP address.

        Returns:
            str: The IP address of the domain if it is valid and reachable.
            str: The original domain if the IP address is not valid or reachable.
            None: If the domain is not reachable.
        """
        try:
            resp = self.dig(domain)
            # 若源IP有效，则不更新
            if resp.returncode == 0:
                ip_pattern = r'\d+\.\d+\.\d+\.\d+'
                # ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                match = re.search(ip_pattern, resp.stdout)
                if match:
                    old_ip = match.group()
                    if self.curl(old_ip, timeout=3):
                        return old_ip
        except Exception as e:
            print(f'err {e}')
            pass
        return
