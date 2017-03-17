# -*- coding: utf-8 -*-
import requests


def main():
    # url = 'http://127.0.0.1:5000/api/package/file/57e7786e-976c-48ec-b643-5d2a5239fc26'
    url = 'http://127.0.0.1:5000/api/project/download/test1_vrf'
    resp = requests.get(url, headers={'Range': 'bytes=0-3'})
    print resp.text
    print resp.status_code
    resp = requests.get(url, headers={'Range': 'bytes=3-'})
    print resp.text
    print resp.headers


if __name__ == '__main__':
    main()