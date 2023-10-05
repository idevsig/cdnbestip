# DomainBest

获取最优的 [Gcore IP](https://api.gcore.com/cdn/public-ip-list) 和 [CloudFlare IP](https://www.cloudflare.com/ips/)。

## 安装

```bash
pip install -r requirements.txt

export CLOUDFLARE_TOKEN=''
export BARK_TOKEN=''
export GCORE_DOMAIN='gcore.xxx.xyz'
export CLOUDFLARE_DOMAIN='cloudflare.xxx.xyz'
        
# 若未设置上述 Token，则只统计有效的 IP 数
python run.py
```

## 使用
依赖 `CloudFlare` 提供的 `DNS` 服务，将使用对应的 `CDN` 服务的域名，`CNAME` 至上述设定的域名（`GCORE_DOMAIN`, `CLOUDFLARE_DOMAIN`）。