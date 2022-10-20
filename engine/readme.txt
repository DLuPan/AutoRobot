获取变量
{}-- 获取变量

tag
XPATH
ID


动作：[]

_CLICK:""// 点击
_INPUT:""// 输入【自动清空】
_APPEND:""// 追加【在原有内容里追加】
_GET_VALUE:"变量名称"// 获取值，回将结果返回到context中
_GET_FOR_NET:{}// 从网络取值 TIMEOUT,指的是事件超时事件，不是指网络超时时间
    URI:地址
    METHOD:请求方式
    TIMEOUT:事件超时时间【时间范围内，回不停的请求网络获取数据】，单位毫秒
    PARAM:请求阐述
    R_PARAM:返回参数定义名称
_WAIT_TAG:{}// 等待tag生成动作，TIMEOUT为等待超时时间，单位s

_WAIT:{}// 单纯的等待时间
"_GET_FOR_NET": {
  "URI": "",
  "METHOD": "GET",
  "TIMEOUT": 1000,
  "PARAM": {
    "email": "{email}"
  },
  "R_PARAM": "RES_URI"
}

{key} 自动注入字符串
_OBJ{key} 获取对象
"_OBJ{smart_code.code}" 获取对象属性
smart_code.code[0][0].name


整理相关笔记
https://jingyan.baidu.com/article/48b558e3fae9657f39c09a5f.html
https://www.cnblogs.com/linkenpark/p/11676297.html
https://blog.csdn.net/kelanmomo/article/details/82886718
https://blog.csdn.net/qq_31683775/article/details/104847566
https://www.jianshu.com/p/632eaae1f158
https://www.jb51.net/article/139159.htm