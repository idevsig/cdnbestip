# CDN Best IP

获取最优的 [Gcore IP](https://api.gcore.com/cdn/public-ip-list) 和 [CloudFlare IP](https://www.cloudflare.com/ips/)。

## 1. 设置环境变量

```bash
# Bark 通知环境变量 https://github.com/finb/bark
export BARK_TOKEN=''
# Chanify 通知环境变量 https://github.com/chanify/chanify
export CHANIFY_TOKEN=''

# CloudFlare Token https://www.cloudflare.com/
export CLOUDFLARE_TOKEN=''

export GCORE_VALID_SKIP='true' # 设置此值时，若 GCORE_DOMAIN 可访问，则不重新获取IP
export GCORE_DOMAIN='gcore.xxx.xyz'

export CLOUDFLARE_VALID_SKIP='true' # 设置此值时，若 CLOUDFLARE_DOMAIN 可访问，则不重新获取IP
export CLOUDFLARE_DOMAIN='cloudflare.xxx.xyz'
export CLOUDFLARE_RANDOM_NUM=2 # 每个IP段随机取几个数值，不设置则默认3
```

## 2. 使用

```bash
pip install -r requirements.txt
python run.py
```

**注意：**

1. 依赖系统的 `ping` 命令。

   ```bash
   # Debian 系
   apt install iputils-ping
   ```

2. 依赖 `CloudFlare` 提供的 `DNS` 服务。
3. 将使用对应的 `CDN` 服务的域名，`CNAME` 至上述设定的域名（`GCORE_DOMAIN`, `CLOUDFLARE_DOMAIN`）。

**设置定时任务，每日检测最新的可用 IP**  
部署到云服务器上，使用 crontab 定时执行，参考相关脚本 [cron](cron)。

## 支持[青龙面板](https://github.com/whyour/qinglong)

1.  `依赖管理` -> `Python` -> 添加依赖 `cloudflare`。
2.  `依赖管理` -> `Linux` -> 添加依赖 `iputils-ping`（`debian` 镜像）。
3.  相关命令查看 **[官方教程](https://github.com/whyour/qinglong#%E5%86%85%E7%BD%AE%E5%91%BD%E4%BB%A4)**。

    ```bash
    ql repo https://github.com/devdoz/cdnbestip.git 'cloudflare|gcore' 'run' 'check|dns_cf' main

    # 或（不建议部署至海外平台，否则不确定该 IP 对国内有效）
    ql repo https://github.com/devdoz/cdnbestip.git 'cloudflare|gcore' 'run' 'check|dns_cf' main
    ```
