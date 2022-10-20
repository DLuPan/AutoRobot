var request = new XMLHttpRequest();
var answerData = arguments[0], isSucc = false, idx = 0;
var desMap = new Map();

answerData.stems.forEach(function (stems) {
    var answerMap = new Map();
    stems.options.forEach(function (option) {
        answerMap.set(option.optionText, option.answer);
    });
    desMap.set(stems.description, answerMap);
});

while (!isSucc) {
    try {
        startAnswer();
        isSucc = true;
    } catch (e) {
        console.log("失败重试", e);
        idx++;
    }

    if (idx > 3) {
        console.log("失败重试超过3次取消执行");
        isSucc = true;
    }
}

function startAnswer() {
// 开始进行自动答题
    var testAnswers = document.getElementsByClassName("paper-stem");
    for (var i = 0; i < testAnswers.length; i++) {
        // 题目
        var questionName = testAnswers[i].getElementsByClassName("question-name")[0]
            .getElementsByClassName("white-space")[0].innerText;
        var answerMap = desMap.get(questionName);
        if (answerMap == null) {
            console.log("没有找到【" + questionName + "】答案");
            continue;
        }

        // 题干
        var questionOptions = testAnswers[i].getElementsByClassName("question-option");

        for (var j = 0; j < questionOptions.length; j++) {
            var labelElement = questionOptions[j].getElementsByTagName("label")[0];
            var questionOptionName = questionOptions[j].getElementsByClassName("white-space")[0].innerText;
            var tgOptionName = questionOptionName.replace(/^[A-Z][.][\s]*/, "");
            if (answerMap.get(tgOptionName)) {
                var labelCs = labelElement.getAttribute("class");
                labelElement.setAttribute("class", labelCs + " lfs-checked-tag");
                questionOptions[j].style.cssText = "background-color: blue;color: #fff;";
                console.log("选中【" + questionOptionName + "】答案");
            }

        }
    }
}
