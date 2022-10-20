/*
* 目的实现答案组装
* 课代表专用脚本
* */

var answerInfo = new Object();
var isSucc = false, idx = 1;

while (!isSucc) {
    try {
        makeAnswerinfo();
        isSucc = true;
        console.log("================================");
        console.log(JSON.stringify(answerInfo));
        console.log("================================");
        console.log("注意将json保存至服务器");
    } catch (e) {
        console.log("失败重试", e);
        idx++;
    }
    if (idx > 5) {
        console.log("重试超过5次结束");
        isSucc = true;
    }
}

/**
 * 组装答案
 */
function makeAnswerinfo() {
    answerInfo = new Object();
    var stems = new Array();
    // 开始组装答案
    var testQuestion = document.getElementsByClassName("paper-stem");
    for (var i = 0; i < testQuestion.length; i++) {
        var stem = new Object();
        // 题目
        var questionName = testQuestion[i].getElementsByClassName("question-name")[0]
            .getElementsByClassName("white-space")[0].innerText;
        stem["description"] = questionName;
        var options = new Array();

        // 题干
        var questionOptions = testQuestion[i].getElementsByClassName("question-option");

        for (var j = 0; j < questionOptions.length; j++) {
            var labelElement = questionOptions[j].getElementsByTagName("label")[0];
            var questionOptionName = questionOptions[j].getElementsByClassName("white-space")[0].innerText;
            var tgOptionName = questionOptionName.replace(/^[A-Z][.][\s]*/, "");
            var option = new Object();
            option["optionText"] = tgOptionName;
            if (labelElement.className.indexOf('is-checked') !== -1) {
                // 表示选中答案是true
                option["answer"] = true;
            } else {
                option["answer"] = false;
            }
            options.push(option);
        }
        stem["options"] = options;
        stems.push(stem);
    }
    answerInfo["stems"] = stems;
}