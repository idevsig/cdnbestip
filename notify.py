import os
import json
import threading
import requests


def bark(title, content, config):
    """
    Send a notification using Bark API.
    """
    if not config.get("token"):
        return

    headers = {'Content-Type': 'application/json'}
    serv_url = 'https://api.day.app' if not config.get("url") else config.get("url")
    url = f'{serv_url}/push'
    data = {
        "title": title,
        "body": content,
        # "group": 'group',
        # "copy": 'copy',
        "device_key": config.get("token"),
    }
    try:
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print('Bark 推送成功')
        else:
            print('Bark 推送失败')
    except Exception as e:
        print('发送通知时出错:', str(e))


def chanify(title, content, config):
    """
    Send a notification using Chanify API.
    https://github.com/chanify/chanify
    """
    if not config.get("token"):
        return
    serv_url = 'https://api.chanify.net' if not config.get("url") else config.get("url")
    url = f'{serv_url}/v1/sender/{config.get("token")}'
    data = {
        "text": content,
    }
    try:
        response = requests.post(
            url=url, data=data)
        if response.status_code == 200:
            print('Chanify 推送成功')
        else:
            print('Chanify 推送失败')
    except Exception as e:
        print('发送通知时出错:', str(e))


def notify(title, content, method, config):
    if method == 'bark':
        bark(title, content, config)
    elif method == 'chanify':
        chanify(title, content, config)


def load_config():
    push_config = {}
    if os.getenv('BARK_TOKEN'):
        push_config['bark'] = {
            "url": os.getenv("BARK_URL"),
            "token": os.getenv('BARK_TOKEN'),
        }
    if os.getenv("CHANIFY_TOKEN"):
        push_config['chanify'] = {
            "url": os.getenv("CHANIFY_URL"),
            "token": os.getenv('CHANIFY_TOKEN'),
        }
    return push_config


def send(title, content):
    push_config = load_config()
    threads = []
    for method, config in push_config.items():
        if config:
            thread = threading.Thread(target=notify, args=(title, content, method, config))
            threads.append(thread)
            thread.start()

    [thread.join() for thread in threads]


if __name__ == "__main__":
    send("标题", "内容")
