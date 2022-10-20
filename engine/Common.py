# --encoding:utf-8--
# 公共文件
from selenium.webdriver.common.by import By

E_TAG_REF = {
    "ID": By.ID,
    "XPATH": By.XPATH,
    "LINK_TEXT": By.LINK_TEXT,
    "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
    "NAME": By.NAME,
    "TAG_NAME": By.TAG_NAME,
    "CLASS_NAME": By.CLASS_NAME,
    "CSS_SELECTOR": By.CSS_SELECTOR
}


def getTagType(tag):
    if tag.find('_SUFFIX') != -1:
        tag = tag[:tag.find('_SUFFIX')]
    return E_TAG_REF[tag]
