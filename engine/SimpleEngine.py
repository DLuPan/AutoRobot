# --encoding:utf-8--
# 简单解析引擎处理
import logging
import os
from typing import List, Dict

from selenium import webdriver

from engine import Action, Event
from simpleutil import SimpleFile

# 初始化日志配置
log = logging.getLogger(__file__)

E_DEFAULT_CONF = os.path.join(os.path.dirname(__file__), 'conf/default.json')


class FlowConfig(object):
    def __init__(self, FlowName):
        self.FlowName = FlowName


class Engine(object):
    def __init__(self, driver: webdriver, context: Dict, confPath=E_DEFAULT_CONF, confJson: Dict = None):
        self.confPath = confPath
        self.driver: webdriver = driver
        self.context: Dict = context
        self.events: List[Event.Event] = []
        self.confJson: Dict = confJson

    def parse(self):
        """
        将文件配置初初始化为Engine对象,如果直接提供了配置对象，就取配置对象就好了
        :return:
        """
        if self.confJson is None:
            _confJson = SimpleFile.fileToJson(self.confPath)
        else:
            _confJson = self.confJson
        _events = self.parseEvent(_confJson['Events'])
        [self.events.append(event) for event in _events]
        self.context['E_ID'] = _confJson['FlowName']
        pass

    def start(self):
        """
        执行流程
        :return:
        """
        try:
            for event in self.events:
                log.info("【SimpleEngin】流程[%s] - 事件[%s]", self.context['E_ID'], event.name)
                event.execute()
                pass
        finally:
            self.driver.close()
            pass

    def parseEvent(self, events: Dict) -> List[Event.Event]:
        eventList = []
        for name, eventItem in events.items():
            _actions = dict(eventItem['Actions'])
            _actionsList = self.parseAction(_actions)
            _p_tag = dict(eventItem['p_tag'])
            event = Event.Event(self.driver, self.context, _actionsList, eventItem['page'], _p_tag, name)
            eventList.append(event)
        if len(eventList) == 0:
            raise Exception("未注册事件")
        return eventList

    def parseAction(self, actions: Dict) -> List[Action.Action]:
        actionList = []
        for name, actionItem in actions.items():
            _tag = dict(actionItem['tag'])
            actions = dict(actionItem['acts'])
            [actionList.append(Action.InitAction(self.driver, self.context, key, value, _tag, name)) for key, value in actions.items()]
        if len(actionList) == 0:
            raise Exception("未绑定动作")
        return actionList


if __name__ == '__main__':
    pass
