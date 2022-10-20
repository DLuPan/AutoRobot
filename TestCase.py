# --encoding:utf-8--
# 提供基础测试
import os
from simpleutil import SimpleUtil
import requests
import json

if __name__ == '__main__':
    _start = SimpleUtil.second()
    context={}
    while not SimpleUtil.isTimeOut(_start):
        resp = requests.request('get', 'http://127.0.0.1:12580/getSmartCode?phone=15700763932&sign=545826eee44ff0cadaa8077e503abc47', params={})
        if resp.status_code == 200:
            context['R_PARAM'] = SimpleUtil.strToJson(resp.text)
