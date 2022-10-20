# --encoding:utf-8--
# 简单解析引擎动作
from abc import ABCMeta, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict
import requests
from simpleutil import SimpleUtil
from simpleutil import SimpleFile
from engine import Common
import time


class Action(metaclass=ABCMeta):
    def __init__(self, driver: webdriver, context: Dict, value, tag: Dict, name='default'):
        self.driver: webdriver = driver
        self.context = context
        self.value = value
        self.tag: Dict = tag
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

    @abstractmethod
    def action(self, element: WebElement):
        """
        具体的执行动作
        :return:
        """
        pass


class ClickAction(Action):
    def action(self, element: WebElement):
        ActionChains(self.driver).click(element).perform()


class ContextClickAction(Action):
    def action(self, element: WebElement):
        ActionChains(self.driver).context_click(element).perform()


class InputAction(Action):
    def action(self, element: WebElement):
        try:
            element.clear()
        except:
            pass
        ActionChains(self.driver).send_keys_to_element(element, self.value).perform()


class AppendAction(Action):
    def action(self, element: WebElement):
        if element.tag_name == 'input':
            text = element.get_attribute('value')
        else:
            text = element.text()
        if not text is None:
            text += self.value
        else:
            text = self.value
        try:
            element.clear()
        except:
            pass
        ActionChains(self.driver).send_keys_to_element(element, text).perform()


class GetValueAction(Action):
    def action(self, element: WebElement):
        if element.tag_name == 'input':
            value = element.get_attribute('value')
        else:
            value = element.text
        self.context[self.value] = value


class GetForNetAction(Action):
    def action(self, element: WebElement):
        _start = SimpleUtil.second()
        while not SimpleUtil.isTimeOut(_start, self.value['TIMEOUT']):
            resp = requests.request(self.value['METHOD'], self.value['URI'], params=self.value['PARAM'])
            if resp.status_code == 200:
                self.context[self.value['R_PARAM']] = SimpleUtil.strToJson(resp.text)
                return
        raise Exception("获取超时")


class ScriptAction(Action):
    def action(self, element: WebElement):
        for type, value in self.value.items():
            if type == '_TEXT':
                self.textScript(value['script'], value['param'])
            elif type == '_FILE':
                self.fileScript(value['script'], value['param'])

    def textScript(self, text, param):
        self.driver.execute_script(text + "return 'None';", param)

    def fileScript(self, path, param):
        script = SimpleFile.fileToStr(path)
        self.driver.execute_script(script + "return 'None';", param)


class WaitTagAction(Action):
    def action(self, element: WebElement):
        _wait_time = self.value['WAIT_TIME']
        for type, value in self.value['WAIT_TAG'].items():
            Wait(self.driver, _wait_time).until(EC.presence_of_all_elements_located((Common.getTagType(type), value)))
        pass


class WaitAction(Action):
    def action(self, element: WebElement):
        time.sleep(self.value['WAIT_TIME'])


def InitAction(driver: webdriver, context: Dict, type, value, tag, name) -> Action:
    if type.find('_SUFFIX') != -1:
        type = type[:type.find('_SUFFIX')]
    if type == "_CLICK":
        return ClickAction(driver, context, value, tag, name)
    elif type == "_CONTEXT_CLICK":
        return ContextClickAction(driver, context, value, tag, name)
    elif type == "_INPUT":
        return InputAction(driver, context, value, tag, name)
    elif type == "_APPEND":
        return AppendAction(driver, context, value, tag, name)
    elif type == "_GET_VALUE":
        return GetValueAction(driver, context, value, tag, name)
    elif type == "_GET_FOR_NET":
        return GetForNetAction(driver, context, value, tag, name)
    elif type == "_SCRIPT":
        return ScriptAction(driver, context, value, tag, name)
    elif type == "_WAIT_TAG":
        return WaitTagAction(driver, context, value, tag, name)
    elif type == "_WAIT":
        return WaitAction(driver, context, value, tag, name)
    return None
