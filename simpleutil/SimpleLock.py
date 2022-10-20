# --encoding:utf-8--
# "简单Lock实现"
import os

from simpleutil import SimpleFile
from simpleutil import SimpleUtil

# 初始化日志配置

class SimpleLock(object):
    def __init__(self, obj, lockDir=None, timeout=10 * 60 * 1000):
        """
        初始化key
        :param obj:
        """
        if not isinstance(obj, str):
            raise Exception("加锁对象只能为字符串")
        self.sign = SimpleUtil.md5(obj)
        self.startTime = SimpleUtil.second()
        self.is_lock = False
        self.tg_path = lockDir + "/lock/" + self.sign
        self.timeout = timeout

    def lock(self):
        _start_time = SimpleUtil.second()
        while not SimpleUtil.isTimeOut(_start_time, self.timeout):
            try:
                if not SimpleFile.exist(os.path.dirname(self.tg_path)):
                    os.makedirs(os.path.dirname(self.tg_path))
                """默认超时时间是10分钟"""
                if not SimpleFile.exist(self.tg_path):
                    """表示能够加锁"""
                    os.makedirs(self.tg_path)
                    self.is_lock = True
                    return True
            except:
                pass
        raise Exception("加锁超时异常")

    def unlock(self):
        if self.is_lock:
            """表示可以锁"""
            if SimpleFile.exist(self.tg_path):
                os.rmdir(self.tg_path)
            self.is_lock = False


if __name__ == '__main__':
    pass
