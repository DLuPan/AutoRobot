# --encoding:utf-8--
# 提供365简单的考试启动服务
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List

import requests

import SeleniumHubServer
import Smart365Common
from engine import SimpleEngine
from simpleutil import SimpleFile, SimpleLock, SimpleUtil

# 初始化日志配置
log = logging.getLogger(__file__)

"""部分全局中间值"""
_answerMap_global = {}  # 考试答案MAP
_object_global = ''  # 考试科目
_exam_boundId_global = ''  # 考试科目的boundId
_exam_id_global = ''  # 考试科目的Id

"""初始化基础配置"""


def initUserList():
    """
    初始化待考列表
    :return:
    """
    global _answerMap_global, _object_global, _exam_boundId_global, _exam_id_global
    # 1、判断考试科目是否更新，未更新，中止30s再说
    _fd_name = datetime.now().strftime("%Y%m%d") + ".json"
    _tg_path = os.path.join(Smart365Common.common_msgDir, 'answer/' + _fd_name)
    _start_time = SimpleUtil.second()
    while True:
        if not os.path.exists(_tg_path):
            log.info("目标[%s]不存在,请等待...", _tg_path)
            time.sleep(30)
            if SimpleUtil.isTimeOut(_start_time, 60 * 60 * 1000):
                raise Exception("初始化用户列表超时")
        else:
            with open(_tg_path, mode='r', encoding='utf-8') as _anwserTemp:
                _answerMap = json.load(_anwserTemp)
            break

    # 初始化全局变量
    _answerMap_global = _answerMap
    _exam_id_global = _answerMap['exam_id']
    _exam_boundId_global = _answerMap['exam_boundId']
    _object_global = _answerMap['object']

    # 判断考试目录是否存在,目前只支持单日单考试科目
    _object = _answerMap['object']
    _objectMap = {}
    _waitUsers = []

    # 提供一个全局锁,避免多次读取
    _lock = SimpleLock.SimpleLock(SimpleUtil.md5(_object), lockDir=Smart365Common.common_baseDir)
    _tg_path = os.path.join(Smart365Common.common_msgDir, 'object/' + SimpleUtil.md5(_object) + '.json')
    if not SimpleFile.exist(_tg_path):
        try:
            _lock.lock()
            # 不存在所以需要初始化考试
            # 更具配置的用户列表更新考试用户列表
            _users = SimpleFile.fileToJson(Smart365Common.common_confDir + "/users.json")['users']
            if len(_users) == 0:
                raise Exception("不存在待考科目")
            for user in _users:
                user['object'] = _object
                if user['isMG']:
                    # 是管理员不用考试
                    user['status'] = 2
                else:
                    user['status'] = 0
                    _waitUsers.append(user)
            _objectMap['object'] = _object
            _objectMap['sign'] = SimpleUtil.md5(_object)
            _objectMap['users'] = _users
            _objectMap['waitUsers'] = _waitUsers
            _objectMap['waitTotal'] = len(_waitUsers)
            SimpleFile.createEmptyJsonFile(_tg_path)
            SimpleFile.jsonToFile(_tg_path, _objectMap)
        finally:
            _lock.unlock()
    else:
        # 已经存在不用处理。
        pass


def getWaitUsers(object) -> List:
    """
    获取当前科目的等待考试用户数
    :param objct:
    :return:
    """
    _tg_path = os.path.join(Smart365Common.common_msgDir, 'object/' + SimpleUtil.md5(object) + '.json')
    _o_lock = SimpleLock.SimpleLock(object, lockDir=Smart365Common.common_baseDir)
    try:
        _o_lock.lock()
        _objectMap = SimpleFile.fileToJson(_tg_path)
    finally:
        _o_lock.unlock()
    if _objectMap['waitTotal'] <= 0:
        return []
    return list([_wait_exec_user for _wait_exec_user in _objectMap['waitUsers'] if _wait_exec_user['status'] == 0])


def getUser(object, phone):
    """
    获取当前科目的用户信息
    :param object:
    :param phone:
    :return:
    """
    _tg_path = os.path.join(Smart365Common.common_msgDir, 'object/' + SimpleUtil.md5(object) + '.json')
    _o_lock = SimpleLock.SimpleLock(object, lockDir=Smart365Common.common_baseDir)
    try:
        _o_lock.lock()
        _objectMap = SimpleFile.fileToJson(_tg_path)
    finally:
        _o_lock.unlock()
        pass
    """获取用户组数据"""
    _users = _objectMap['users']
    """获取当前用户"""
    _t_user = [_userTemp for _userTemp in _users if _userTemp['phone'] == phone][0]
    return _t_user


def updateUser(user: Dict):
    """
    更新用户信息
    :param user:
    :return:
    """
    # 用户表锁，避免因为当前操作导致的数据不一致
    _o_lock = SimpleLock.SimpleLock(user['object'], lockDir=Smart365Common.common_baseDir)
    _tg_path = os.path.join(Smart365Common.common_msgDir, 'object/' + SimpleUtil.md5(user['object']) + '.json')
    try:
        _o_lock.lock()
        _objectMap = SimpleFile.fileToJson(_tg_path)
        """获取当前用户组"""
        _users = list(_objectMap['users'])
        """获取当前等待用户组"""
        _waitUsers = list(_objectMap['waitUsers'])
        """获取当前用户组-用户数据"""
        _t_user = [_userTemp for _userTemp in _users if _userTemp['phone'] == user['phone']][0]
        """获取当前等待组-用户数据"""
        _t_waitUser = [_userTemp for _userTemp in _waitUsers if _userTemp['phone'] == user['phone']][0]

        """更新用户状态"""
        _t_user['status'] = user['status']
        _t_waitUser['status'] = user['status']
        """等待用户组删除等待用户数据【成功or失败删除】"""
        if user['status'] == -1 or user['status'] == 2:
            _waitUsers.remove(_t_waitUser)
        """更新用户表数据【全局】"""
        _objectMap['users'] = _users
        _objectMap['waitUsers'] = _waitUsers
        _objectMap['waitTotal'] = len(_waitUsers)
        SimpleFile.jsonToFile(_tg_path, _objectMap)
        pass
    finally:
        _o_lock.unlock()
    pass


def noticeError(phone, object, msg=''):
    """
    通知用户考试失败
    :param phone:
    :param object:
    :return:
    """
    body = {
        "msgtype": "text",
        "text": {
            "content": "[%s]考试中异常，请立刻手动登录[https://studysmart365.foresealife.com/login]确认。异常信息：%s." % (object, msg),
            "mentioned_mobile_list": [phone]
        }
    }
    sendWXBot(body)


def noticeSucc(phone, object, msg=''):
    """
    通知用户考试成功
    :param phone:
    :param object:
    :param msg:
    :return:
    """
    body = {
        "msgtype": "text",
        "text": {
            "content": "当前科目[%s]考试结果：%s." % (object, msg),
            "mentioned_mobile_list": [phone]
        }
    }
    sendWXBot(body)


def noticeSetMartCode(phone, object, msg=''):
    """
    通知用户设置smart_code
    :param phone:
    :param object:
    :param msg:
    :return:
    """
    body = {
        "msgtype": "text",
        "text": {
            "content": "考试登录中，请拼接你的验证并提交：%s?phone=%s&sign=%s&code=验证码." % (Smart365Common.common_server_config['setSmartCode_uri_global'], phone, SimpleUtil.md5(object)),
            "mentioned_mobile_list": [phone]
        }
    }
    sendWXBot(body)


def sendWXBot(body: Dict):
    log.info("请求地址：[%s]", Smart365Common.common_server_config['webHook_uri_global'])
    log.info("请求参数：[%s]", body)
    resp = requests.post(Smart365Common.common_server_config['webHook_uri_global'], json=body)
    if resp.status_code == 200:
        log.info('消息发送成功')
    else:
        log.error('消息发送失败')


def loop():
    """
    考试方法，gogogog
    考试用户状态：0、初始化，1、考试中，-1、考试失败，2、考试成功
    :return:
    """
    # 构建考试用上下文对象
    _context = {
        "_answerMap": _answerMap_global,
        "exam_boundId": _exam_boundId_global,
        "exam_id": _exam_id_global,
        "object": _object_global,
        "sign": SimpleUtil.md5(_object_global),
        "getSmartCodeUri": Smart365Common.common_server_config['getSmartCode_uri_global'],
        "_baseDir": Smart365Common.common_baseDir
    }
    log.info("当前考试科目：%s", _object_global)
    while True:
        """直到待考用户变为0才能终止循环"""
        _users = getWaitUsers(_object_global)
        _wait_num = len(_users)
        log.info("当前待考用户数：%s", _wait_num)
        if _wait_num == 0:
            break
        for _user in _users:
            _phone = _user['phone']
            _name = _user['name']
            _login_type = _user['loginType']
            log.info("当前考试用户：%s,手机号：%s,登陆方式：%s", _name, _phone, _login_type)
            # 创建当前的用户锁
            _u_lock = SimpleLock.SimpleLock(_phone, timeout=1000, lockDir=Smart365Common.common_baseDir)
            try:
                _u_lock.lock()
                """再次获取避免加锁中途变更"""
                _n_user = getUser(_object_global, _phone)
                _status = _n_user['status']
                if _status == 0:
                    _n_user['status'] = 1
                    updateUser(_n_user)
                    """开始考试，其他状态不考试的【初始化上线文对象】"""
                    _context['phone'] = _n_user['phone']
                    """初始化引擎'--headless',"""
                    _options = ['--disable-gpu', '--allow-popups-during-page-unload']
                    _driver = SeleniumHubServer.getWebDriver(_options=_options)
                    try:
                        _confJson = SimpleFile.fileToJson(os.path.join(Smart365Common.common_confDir, _n_user['flow']))
                        engine = SimpleEngine.Engine(_driver, _context, confJson=_confJson)
                        engine.parse()
                        """开始跑脚本【】"""
                        noticeSetMartCode(_n_user['phone'], _object_global)
                        engine.start()
                        _driver.quit()
                        _n_user['status'] = 2
                        noticeSucc(_n_user['phone'], _object_global, msg=_context['exec_res'])
                    except Exception as err:
                        _driver.quit()
                        log.exception("执行考试异常")
                        _n_user['status'] = -1
                        noticeError(_n_user['phone'], _object_global, msg=err)
                    updateUser(_n_user)
            except:
                log.exception("失败")
                pass
            finally:
                _u_lock.unlock()

        pass
    pass


def start():
    """
    考试服务启动
    :return:
    """
    # 初始化代考用户列表
    initUserList()
    # 执行考试方法
    loop()
    pass


if __name__ == '__main__':
    """简单测试逻辑"""
    pass
