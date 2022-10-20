# --encoding:utf-8--
# 课代表平台，主要作用实现对答案的采集相关工作
# 相关依赖安装
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple paramiko
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scp
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller

import json
import logging
import time
from datetime import datetime

import paramiko
from scp import SCPClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from simpleutil import LocalLog

# 初始化日志配置
LocalLog.initLogConf()
log = logging.getLogger(__file__)

SMART_LOGIN_URI = "https://studysmart365.foresealife.com/login"

CHROME_DRIVER_PATH = {"WIN": "./driver/chromedriver.exe",
                      "LINUX": "./driver/chromedriver"}


class class_platform(object):
    # 课代表平台
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-infobars")
        self.browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH['WIN'], chrome_options=chrome_options)
        self.action = ActionChains(self.browser)
        pass


class scp_client(object):
    def __init__(self):
        with open("conf/application.json", encoding="utf-8", mode="r+") as _conf:
            app_conf = json.load(_conf)
        self.SERVER_IP = app_conf.get("SERVER_IP", "")
        self.SERVER_USER = app_conf.get("SERVER_USER", "")
        self.SERVER_PWD = app_conf.get("SERVER_PWD", "")
        self.SERVER_RES_PATH = app_conf.get("SERVER_RES_PATH", "")
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh_client.connect(self.SERVER_IP, 22, self.SERVER_USER, self.SERVER_PWD)
        self.scp_client = SCPClient(self.ssh_client.get_transport(), socket_timeout=15.0)

    def upload(self, local_path, remote_path=None):
        if remote_path is None:
            remote_path = self.SERVER_RES_PATH
        try:
            self.scp_client.put(local_path, remote_path=remote_path)
        except FileNotFoundError as e:
            log.exception("系统找不到指定文件：%s,%s", local_path, e)
        except Exception as e:
            log.exception("上传异常:%s", e)
        finally:
            return self

    def download(self, remote_path, local_path='./resource'):
        try:
            self.scp_client.get(remote_path, local_path=local_path)
        except Exception as e:
            log.info("下载文件异常:%s", e)
        finally:
            return self

    def close(self):
        self.scp_client.close()


if __name__ == '__main__':
    log.info("课代表专用答题启动")
    platform = class_platform()
    # 打开登录
    platform.browser.get(SMART_LOGIN_URI)
    with open("script/smart_answer_div.js", encoding="utf-8", mode="r+") as _script:
        smart_answer = _script.read()
    while True:
        handles = platform.browser.window_handles
        log.info("全部句柄：%s", handles)
        if len(handles) > 1:
            platform.browser.switch_to_window(handles[1])
            log.info("切换窗口，当前句柄：%s", platform.browser.current_window_handle)
            break
        time.sleep(2)
    # 表示进入考试界面
    while True:
        try:
            platform.browser.find_element_by_xpath("//button/span[contains(text(), '提 交')]")
            platform.browser.execute_script(smart_answer + " return 'True';")
            log.info("已进入考试界面，等待课代表提交")
            break
        except NoSuchElementException as err:
            log.info("暂未进入考试界面，请等待")
            time.sleep(2)

    while True:
        try:
            by_span = platform.browser.find_element_by_id("class_paltform")
            if str(by_span.text).find("已采集") > -1:
                with open("script/smart_answer.js", encoding="utf-8", mode="r+") as _script:
                    smart_answer = _script.read()
                answer_dic = platform.browser.execute_script(smart_answer + " return answerInfo;")
                break
            log.info("课代表增在努力答题")
            time.sleep(2)
        except NoSuchElementException as err:
            log.info("暂未找到，请等待")
            time.sleep(2)

    #  保存answer_dic到文件里
    log.info("当前答案列表:%s", answer_dic)
    _fd_name = datetime.now().strftime("%Y%m%d") + ".json"
    with open("./resource/" + _fd_name, encoding="utf-8", mode="w") as _fd:
        json.dump(answer_dic, _fd, ensure_ascii=False, sort_keys=True, indent=4)
    #  开始上传到服务器
    scp_client().upload("./resource/" + _fd_name).close()
    pass
