# --encoding:utf-8--
# 提供简单的文件操作
import json
import os


def exist(path=None):
    """
    判断path是否存在
    :param path:
    :return:
    """
    if path is None:
        raise Exception("路径不能为None")
    return os.path.exists(path)


def creteDir(path=None):
    """
    创建目标文件夹
    :param path:
    :return:
    """
    if path is None:
        raise Exception("文件夹不能为None")
    if exist(path):
        return None
    return os.makedirs(path)


def createFile(path=None):
    """
    创建目标文件
    :param path:
    :return:
    """
    if path is None:
        raise Exception("文件路径不能为None")
    if not exist(os.path.dirname(path)):
        creteDir(os.path.dirname(path))
    if exist(path):
        raise Exception("文件已经存在")
    open(path, mode='w', encoding='utf-8')


def fileToJson(path=None):
    """
    文件转json
    :param path:
    :return:
    """
    if path is None:
        raise Exception("路径不能为None")
    if not exist(path):
        raise Exception("当前文件["+path+"]不存在")
    with open(path, mode='r', encoding='utf-8') as _file:
        _json = json.load(_file)
    return _json


def fileToStr(path=None):
    if not exist(path):
        raise Exception(path + "当前文件不存在")
    with open(path, mode='r', encoding='utf-8') as _file:
        _str = _file.read()
    return _str


def jsonToFile(path=None, jsonObj=dict):
    """
    json保存到文件
    :param path:
    :param jsonObj:
    :return:
    """
    if path is None:
        raise Exception("路径不能为None")
    if not exist(path):
        raise Exception("目标路径不能为空")
    with open(path, mode='w', encoding='utf-8') as _file:
        json.dump(jsonObj, _file, ensure_ascii=False, sort_keys=True, indent=4)


def createEmptyJsonFile(path=None):
    """
    创建空json文件
    :param path:
    :return:
    """
    createFile(path)
    jsonToFile(path, {})


def deleteFile(path=None):
    if path is None:
        raise Exception("path不能为None")
    if not exist(path):
        raise Exception(path + "路径不存在")
    if not os.path.isfile(path):
        raise Exception(path + "不是文件")
    os.remove(path)


if __name__ == '__main__':
    pass
