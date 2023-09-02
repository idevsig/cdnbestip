import re
import sys
import CloudFlare


def extract_host_and_domain(domain_name):
    '''
    正则表达式模式来匹配主机和域名
    '''
    pattern = r'^(.*?)\.(.*?\.[a-zA-Z]+)$'
    
    # 使用正则表达式模式匹配输入字符串
    match = re.match(pattern, domain_name)
    
    if match:
        host = match.group(1)
        domain = match.group(2)
        return host, domain
    else:
        return None, None
    
def main(ip_address=None, record_name=None, token=None, ):
    # 接收参数
    args = sys.argv[1:]
    # print(f'args: {args}')

    # 查找Zone ID
    try:
        # print(f'ip:{ip_address}, record: {record_name}, token: {token}')
        if not token:
            token = args[0]
        if not record_name:
            record_name = args[1]
        if not ip_address:
            ip_address = args[2]

        print(f'ip:{ip_address}, record: {record_name}, token: {token}')

        host, domain_name = extract_host_and_domain(record_name)
        if not host:
            raise ValueError(f'No valid host')

        cf = CloudFlare.CloudFlare(token=token)
        
        zones = cf.zones.get(params={'name': domain_name})
        # print(zones)
        if zones:
            zone_id = zones[0]['id']
            print(f'Zone ID for {domain_name}: {zone_id}')

      # 要修改的DNS记录的信息
        dns_record_name = record_name  # DNS记录名称
        dns_record_type = 'A'  # DNS记录类型，这里以A记录为例
        dns_record_data = {
            'name': dns_record_name,
            'type': dns_record_type,
            'ttl': 1,  # TTL（生存时间）
            'proxied': False,  # 是否启用Cloudflare代理
            'content': ip_address,  # 新的IP地址
        }

        # print(f'{cf.zones.dns_records.get(zone_id)}')
        # 获取指定名称和类型的DNS记录
        dns_records = cf.zones.dns_records.get(zone_id, params={'name': dns_record_name, 'type': dns_record_type})
        # print(f'dns_records: {dns_records}')
        if dns_records:
            dns_record_id = dns_records[0]['id']
            # 更新DNS记录
            cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record_data)
            print(f'DNS record for {dns_record_name} ({dns_record_type}) IP({ip_address}) updated successfully')
        else:
            # 如果记录不存在，则添加一个新记录
            cf.zones.dns_records.post(zone_id, data=dns_record_data)
            print(f'New DNS record for {dns_record_name} ({dns_record_type}) IP({ip_address}) added successfully')
    except Exception as e:
        print('Error:', str(e))

if __name__ == '__main__':
    main()