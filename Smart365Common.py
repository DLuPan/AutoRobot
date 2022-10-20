# --encoding:utf-8--
# 公共组件，用来确定部分全局信息的
import os

from simpleutil import SimpleFile

"""基础目录配置"""
common_baseDir = ''
common_confDir = ''  # 配置文件目录
common_msgDir = ''  # 消息目录

"""基础配置文件"""
common_server_config = {}


def init(baseDir, confDir, msgDir):
    global common_baseDir, common_confDir, common_msgDir, common_server_config
    common_baseDir = baseDir
    common_confDir = confDir
    common_msgDir = msgDir
    common_server_config = SimpleFile.fileToJson(os.path.join(common_confDir, 'server.json'))
