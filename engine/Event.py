# --encoding:utf-8--
# 简单解析引擎时间
import logging
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait

from engine import Action, Common
from simpleutil import LocalLog, SimpleUtil

# 初始化日志配置
LocalLog.initLogConf()
log = logging.getLogger(__file__)


class Event(object):
    def __init__(self, driver: webdriver, context: Dict, actions: List[Action.Action], page, p_tag: Dict, name='default'):
        """
        初始化事件
        :param driver: 事件驱动器
        :param context:  事件上下文对象
        :param actions: 事件动作集合
        :param page: 事件页面uri
        :param p_tag: 事件页面标识
        """
        self.driver: webdriver = driver
        self.context = context
        self.actions: List[Action.Action] = actions
        self.page = self.paseValue(page)
        self.p_tag = p_tag
        self.name = name

    def paseValue(self, value):
        """
        解析value
        :param value:
        :return:
        """
        if type(value) == str:
            if value.startswith("_OBJ{") and value.endswith("}"):
                return SimpleUtil.getForDict(value[5:-1], self.context)
            return value.format_map(self.context)
        elif type(value) == list:
            for l_value in value:
                l_value = self.paseValue(l_value)
            return value
        elif type(value) == dict:
            keys = value.keys()
            for key in keys:
                value[key] = self.paseValue(value[key])
            return value
        return value

    def execute(self, timeout=120):
        """
        执行事件
        :return:
        """
        self.openPage()
        self.waitLoad(timeout)
        """
        开始执行事件
        """
        for action in self.actions:
            log.info("【SimpleEngin】流程[%s] - 事件[%s] - 动作[%s]", self.context['E_ID'], self.name, action.name)
            _elements = self.parseElement(action.tag)
            # 初始化value值
            action.value = action.paseValue(action.value)
            if len(_elements) == 0:
                action.action(None)
            else:
                [action.action(element) for element in _elements]
        pass

    def openPage(self):
        """
        打开事件所在页面
        :return:
        """
        self.driver.get(self.page)

    def waitLoad(self, timeout):
        """
        判断页面是否加载完成【默认两分钟】
        :return:
        """
        for type, value in self.p_tag.items():
            Wait(self.driver, timeout).until(EC.presence_of_all_elements_located((Common.getTagType(type), value)))

    def parseElement(self, tag: Dict) -> List[WebElement]:
        """
        解析tag
        :param tag:
        :return:
        """
        elements = []
        if len(tag) == 0:
            # 服务于无tag事件
            return elements
        for key, value in tag.items():
            elementLocated = EC.presence_of_all_elements_located((Common.getTagType(key), value))
            [elements.append(element) for element in elementLocated(self.driver)]
        if len(elements) == 0:
            raise Exception("对象不存在")
        return elements
