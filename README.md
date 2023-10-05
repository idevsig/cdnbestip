# CDN Best IP

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

**设置定时任务，每日检测最新的可用 IP**
部署到云服务器上，使用 crontab 定时执行，参考相关脚本 [cron](cron)。

## 使用
依赖 `CloudFlare` 提供的 `DNS` 服务。   
将使用对应的 `CDN` 服务的域名，`CNAME` 至上述设定的域名（`GCORE_DOMAIN`, `CLOUDFLARE_DOMAIN`）。