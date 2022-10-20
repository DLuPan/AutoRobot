# --encoding:utf-8--
# 提供了Smart365管理配置
import sys, getopt, os
import Smart365Common
from simpleutil import LocalLog
import NetServer
import ExamServer

if __name__ == '__main__':
    # Smart365MG.py 启动工具,以及初始化工具，gogogo
    # 启动工具：
    #   Net:启动网络服务【用于接收用户提交的验证码】
    #   Exam:启动考试服务
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['server=', 'base=', 'log=', 'conf=', 'script=', 'msg=', 'port=', 'ip='])
    except getopt.GetoptError:
        print('Smart365MG.py --server <SERVER_NAME> --base <BASE_PATH> --log <LOG_PATH> --conf <CONF_PATH> --script <SCRIPT_PATH> --msg <MSG_PATH>')
        sys.exit(2)

    _SERVER_NAME = None
    _BASE_PATH = None
    _LOG_PATH = None
    _SCRIPT_PATH = None
    _MSG_PATH = None
    _CONF_PATH = None
    _IP = None
    _PORT = None
    for opt, arg in opts:
        if opt == '-h':
            print('Smart365MG.py --server <SERVER_NAME> --base <BASE_PATH> --log <LOG_PATH> --conf <CONF_PATH> --script <SCRIPT_PATH> --msg <MSG_PATH>')
            sys.exit()
        elif opt == '--server':
            _SERVER_NAME = arg
        elif opt == '--base':
            _BASE_PATH = arg
        elif opt == '--log':
            _LOG_PATH = arg
        elif opt == '--conf':
            _CONF_PATH = arg
        elif opt == '--script':
            _SCRIPT_PATH = arg
        elif opt == '--msg':
            _MSG_PATH = arg
        elif opt == '--ip':
            _IP = arg
        elif opt == '--port':
            _PORT = arg

    if _SERVER_NAME is None:
        print('input --server <SERVER_NAME>')
        sys.exit()
    if _BASE_PATH is None:
        print('--base <BASE_PATH>')
        sys.exit()
    if _LOG_PATH is None:
        print('input --log <LOG_PATH>')
        sys.exit()
    if _SCRIPT_PATH is None:
        print('input --script <SCRIPT_PATH>')
        sys.exit()
    if _MSG_PATH is None:
        print('input --msg <MSG_PATH>')
        sys.exit()
    if _CONF_PATH is None:
        print('input --conf <CONF_PATH>')
        sys.exit()

    """初始化全局配置并启动对应服务"""
    # 初始化日志配置
    LocalLog.initLogConf(baseDir=os.path.join(_LOG_PATH, _SERVER_NAME))
    Smart365Common.init(_BASE_PATH, _CONF_PATH, _MSG_PATH)

    if _SERVER_NAME == 'Net':
        if _PORT is None:
            if _IP is None:
                NetServer.start()
            else:
                NetServer.start(ip=_IP)
        else:
            if _IP is None:
                NetServer.start(port=_PORT)
            else:
                NetServer.start(ip=_IP, port=_PORT)
    elif _SERVER_NAME == 'Exam':
        ExamServer.start()
    else:
        print("Not found %s" % _SERVER_NAME)
        sys.exit()
