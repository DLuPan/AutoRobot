# --encoding:utf-8--
# 简单工具集合
import hashlib
import json
import time


def md5(str):
    """
    md5加密方法，提供将str进行加密的方法
    :param str:
    :return:
    """
    m = hashlib.md5()
    b = str.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()
    return str_md5


def getForDict(value: str, context: dict):
    _cur = context
    _cur_key = ''
    _cur_list_key = ''
    _no_list = True
    for c in value:
        if c == '.' and _no_list:
            if _cur_key != '':
                _cur = _cur[_cur_key]
                _cur_key = ''
        elif c == '[':
            if _cur_key != '':
                _cur = _cur[_cur_key]
                _cur_key = ''
            _no_list = False
        elif c == ']':
            _cur = _cur[int(_cur_list_key)]
            _cur_list_key = ''
            _no_list = True
        else:
            if _no_list:
                _cur_key += str(c)
            else:
                _cur_list_key += str(c)
    if _cur_key != '':
        return _cur[_cur_key]
    return _cur


def second():
    """
    获取时间戳
    :return:
    """
    return int(round(time.time() * 1000))


def isTimeOut(startTime, timeOut=60 * 1000):
    if second() - startTime < timeOut:
        return False
    return True


def strToJson(text: str):
    """
    字符串转json
    :param text:
    :return:
    """
    return json.loads(text, encoding='UTF-8')


if __name__ == '__main__':
    pass
