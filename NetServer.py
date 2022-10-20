# --encoding:utf-8--
# 提供365简单的网络服务
import logging
import os
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

import Smart365Common
from simpleutil import SimpleFile
from simpleutil import SimpleLock
from simpleutil import SimpleUtil

# 初始化日志配置
log = logging.getLogger(__file__)

def setSmsCode(phone, sign, code):
    if code is None or len(code) != 6:
        log.error("输入code有问题")
        return False
    """初始化sms code配置"""
    smscodeEntry = {}
    smscodeEntry['code'] = code
    smscodeEntry['version'] = 0
    smscodeEntry['is_valid'] = True
    lock = SimpleLock.SimpleLock("SMSCODE" + phone, lockDir=Smart365Common.common_baseDir)
    _tg_path = os.path.join(Smart365Common.common_msgDir, "smscode/" + phone + ".json")
    try:

        lock.lock()
        if not SimpleFile.exist(_tg_path):
            SimpleFile.createFile(_tg_path)
            smscodes = {}
        else:
            smscodes = SimpleFile.fileToJson(_tg_path)
        if sign in smscodes.keys():
            smscodeEntry['version'] = len(smscodes[sign])
            smscodes[sign].append(smscodeEntry)
        else:
            smscodes[sign] = [smscodeEntry]
        SimpleFile.jsonToFile(_tg_path, smscodes)
    except:
        log.exception("保存SMS CODE失败")
        return False
    finally:
        lock.unlock()
    return True


def getSmsCode(phone, sign, timeout=10000):
    """
    获取验证码
    :param phone:
    :param sign
    :param timeout 超时时间，默认2分钟
    :return:
    """
    # 从msg/smscode/md5(object),列表中获取消息，同时带version走
    # smscode：sign：[code，version]
    # 开始加载
    code = None
    _startTime = SimpleUtil.second()
    _tg_path = os.path.join(Smart365Common.common_msgDir, "smscode/" + phone + ".json")
    """加锁"""
    lock = SimpleLock.SimpleLock("SMSCODE" + phone, lockDir=Smart365Common.common_baseDir)
    while code is None and not SimpleUtil.isTimeOut(_startTime, timeout):
        if not SimpleFile.exist(_tg_path):
            time.sleep(2)
            continue
        try:
            lock.lock()
            smscodes = SimpleFile.fileToJson(_tg_path)
            smscodeEntrys = smscodes[sign]
            if len(smscodeEntrys) <= 0:
                time.sleep(2)
                continue
            version = 0

            """获取当前code，如果没有就不用更新"""
            for _smscodeEntry in smscodeEntrys:
                if _smscodeEntry['version'] >= version and _smscodeEntry['is_valid']:
                    code = _smscodeEntry['code']
                    _smscodeEntry['is_valid'] = False
            smscodes[sign] = smscodeEntrys
            """更新信息"""
            if code is not None:
                """开始更新配置"""
                SimpleFile.jsonToFile(_tg_path, smscodes)
        finally:
            lock.unlock()
    return code


class GetParse(object):
    def __init__(self, path: str):
        if path.find('?') != -1:
            self.path = path[:path.find('?')]
            try:
                self.params = dict([p.split('=') for p in path[path.find('?') + 1:].split('&')])
            except:
                self.params = {}
        else:
            self.path = path
            self.params = {}


def getSmartCode(params: dict):
    code = getSmsCode(params['phone'], params['sign'])
    if code is None:
        return {'msg': '获取code异常了'}, 500
    return {'code': code}, 200


def setSmartCode(params: dict):
    if setSmsCode(params['phone'], params['sign'], params['code']):
        return {'msg': '保存成功'}, 200
    return {'msg': '保存失败'}, 500


def route(path: str, params: dict):
    log.info("调用：路径[%s] - 参数[%s]", path, params)
    res = {}
    code = 404
    if path == '/getSmartCode':
        res, code = getSmartCode(params)
    elif path == '/setSmartCode':
        res, code = setSmartCode(params)
    log.info("调用：路径[%s] - 返回值[%s] - 状态码[%s]", path, res, code)
    return res, code


class NetServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """解析参数"""
        res = {}
        code = 404
        try:
            parse = GetParse(self.path)
            res, code = route(parse.path, parse.params)
        except:
            ers = {'msg': '服务器异常'}
            code = 500
            pass
        self.send_response(code)
        self.send_header(
            'Content-type', 'application/json; charset=utf-8')
        self.end_headers()  # 发送\r\n,意味这下一行为报体
        self.wfile.write(bytes(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4), 'utf-8'))


def start(ip='127.0.0.1', port=12580):
    server_address = (ip, port)
    http_server = HTTPServer(server_address, NetServerHandler)
    log.info("启动HTTP服务：ip[%s] - port[%s]", ip, port)
    http_server.serve_forever()


if __name__ == '__main__':
    pass
    # setSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa'), '123456')
    # setSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa'), '678912')
    # print(getSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa')))
    # setSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa'), '123sd')
    # print(getSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa')))
    # setSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa'), '42sdfs56')
    # setSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa'), '32sdfsd6')
    # print(getSmsCode('15700763932', SimpleUtil.md5('测试文章wawawawa')))
