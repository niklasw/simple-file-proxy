#!/usr/bin/env python3

from pathlib import Path
import requests
import uuid

config = {'url': 'http://localhost:5000/transfer'}

def publish(file_path: Path):
    srv = config['url']
    files = {'file': file_path.open('rb')}
    file_name = str(uuid.uuid3(uuid.NAMESPACE_URL, str(file_path)))
    url = '/'.join([srv, file_name])
    try:
        requests.post(url, files=files)
        return url
    except Exception as e:
        print('POST request failed')
        return None


def fetch(file_name, save_as = Path('fetched.data')):
    srv = config['url']
    url = '/'.join([srv, str(file_name)])
    try:
        response = requests.get(url)
        with save_as.open('wb') as f:
            f.write(response.content)
        return url
    except Exception as e:
        print('GET request failed')
        return None


if __name__ == '__main__':
    import sys
    try:
        action = sys.argv[1]
        f = Path(sys.argv[2])
    except:
        print('Missing arguments: Usage ./client.py <post|get> <file>')
        sys.exit(1)
    if action in ['post','get']:
        if action == 'post':
            if f.exists():
                print(publish(f))
            else:
                print(f'File {f} does not exist')
        elif action == 'get':
            print(fetch(f))
    else:
        print(f'Argument eror in {sys.argv}')
