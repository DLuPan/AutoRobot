var button = document.createElement('button');
button.setAttribute('type', 'button');
button.setAttribute('class', 'el-button el-button--danger');
button.setAttribute('onclick', "document.getElementById('class_paltform').innerHTML='课代表专属按钮(已采集)'");
var span = document.createElement('span');
span.setAttribute('id', 'class_paltform');
span.innerHTML = "课代表专属按钮(未采集)";
button.appendChild(span);
var paperButton = document.getElementsByClassName("paper-bottom")[0];
paperButton.appendChild(button);