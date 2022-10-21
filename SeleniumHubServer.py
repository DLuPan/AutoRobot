# --encoding:utf-8--
# seleniumHub服务提供对hub的管理
import json
import logging
import time
from typing import Dict, List

import requests
from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome import options

import Smart365Common
from simpleutil import SimpleUtil

# 初始化日志配置
log = logging.getLogger(__file__)

"""先直接完成chrome再说，其他都是虚假的，只有这个快速完成才是真实的可靠的，有效的，加油好道济"""


def status() -> Dict:
    """获取当前selenium hub状态"""
    resp = requests.request("GET", Smart365Common.common_server_config['selenium_hub_uri'] + "/grid/api/hub")
    if resp.status_code != 200:
        raise Exception("获取hub状态异常，请查看hub状态 %s" % Smart365Common.common_server_config['selenium_hub_uri'] + "/status")
    else:
        _status = json.loads(resp.text)
    return _status


def getWebDriver(sessionId=None, _options: List = None, timeout=60000) -> webdriver:
    """
    获取一个可用的webDriver，暂时可以不用处理不急的
    :param sessionId:
    :param timeout:超时时间
    :return:
    """
    _start_time = SimpleUtil.second()
    while not SimpleUtil.isTimeOut(_start_time, timeout):
        """获取hub状态，判断是否具有可用条件"""
        _status = status()
        """获取可用客户端插槽数量"""
        _slotCounts = _status['slotCounts']
        _total = _slotCounts['total']
        if _total == 0:
            raise Exception("没有可用webdriver客户端，请查看配置")
        _free = _slotCounts['free']
        log.info("当前可用webdriver为：%s", _free)
        if _free == 0:
            """没有可用休眠10s"""
            time.sleep(10)
            continue
        """开始获取webdriver,当前只支持获取chrome的配置"""
        chrome_options = webdriver.ChromeOptions()
        if _options is not None:
            [chrome_options.add_argument(_argument) for _argument in _options]
        try:
            driver = webdriver.Remote(command_executor=Smart365Common.common_server_config['selenium_hub_uri'] + '/wd/hub', options=chrome_options)
            log.info("当前驱动：sessionId[%s] - 容器信息[%s]", driver.session_id, driver.capabilities)
            return driver
        except Exception as err:
            """获取异常，休眠5分钟重新获取"""
            log.exception("获取webdriver异常")
            time.sleep(5)
    raise Exception('获取webdriver异常')


class ReuseBrowser(Remote):
    """
    用已有Session创建driver
    """

    def __init__(self, command_executor, session_id):
        self.r_session_id = session_id
        Remote.__init__(self, command_executor=command_executor, desired_capabilities={})

    def start_session(self, desired_capabilities, browser_profile=None):
        capabilities = {'desiredCapabilities': {}, 'requiredCapabilities': {}}
        for k, v in desired_capabilities.items():
            if k not in ('desiredCapabilities', 'requiredCapabilities'):
                capabilities['desiredCapabilities'][k] = v
            else:
                capabilities[k].update(v)
        if browser_profile:
            capabilities['desiredCapabilities']['firefox_profile'] = browser_profile.encoded

        self.w3c = "specificationLevel" in self.capabilities
        self.capabilities = options.Options().to_capabilities()
        self.session_id = self.r_session_id
        self.w3c = False


def closeDriver(sessionId, url=None):
    """
    提供一个异常关闭driver的工具
    :param sessionId:
    :return:
    """
    try:
        if url is None:
            url = Smart365Common.common_server_config['selenium_hub_uri']
        driver = ReuseBrowser(url + '/wd/hub', sessionId)
        if driver is not None:
            driver.quit()
    except Exception as err:
        log.exception("驱动关闭异常")


if __name__ == "__main__":
    # driver = getWebDriver()
    # driver.get("http://www.baidu.com")
    # print(driver.page_source)
    # driver.quit()
    # _session_list = []
    # _options = ['--headless', '--disable-gpu', '--allow-popups-during-page-unload']
    # for i in range(3):
    #     try:
    #         driver = getWebDriver(_options=_options, timeout=3000)
    #     except:
    #         log.exception("获取异常")
    #         continue
    #         pass
    #     driver.get("http://localhost:4444/grid/api/hub")
    #     print(driver.page_source)
    #     _session_list.append(driver.session_id)
    # for session_id in _session_list:
    #     try:
    #         closeDriver(session_id)
    #     except:
    #         pass
    pass
    # driver = ReuseBrowser("http://10.0.75.1:4444/wd/hub", "1530293e62097bc90dfba6371d8b5ce7")
    # driver.maximize_window()
    # driver.find_element_by_id("kw").send_keys("驱动自动化")
    # driver.find_element_by_id("su").click()
