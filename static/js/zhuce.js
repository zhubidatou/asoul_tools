function doSendMail(obj) {
    var email = $.trim($("#regname").val());
    if (!email.match(/.+@.+\..+/)) {
        bootbox.alert({title: '错误提示', message: "邮箱地址不准确!"})
        return false;
    }
    $(obj).attr('disabled', true);

    $.post('/ecode', 'email=' + email, function (data) {
        if (data == 'email-invalid') {
            bootbox.alert({title: '错误提示', message: '邮箱地址格式不正确'});
            $("#regname").focus();
            return false;
        }
        if (data == 'send-pass') {
            bootbox.alert({title: '信息提示', message: "邮箱验证码已成功发送!"});
            $('#regname').attr('disabled', true);
            $(obj).attr('disabled', true);
            return false;
        } else {
            bootbox.alert({title: '错误提示', message: "验证码未发送成功!"});
            return false;
        }
    })
}

function doReg() {
    var regname = $.trim($("#regname").val());
    var regpass = $.trim($("#regpass").val());
    var regcode = $.trim($("#regcode").val());

    if (!regname.match(/.+@.+\..+/) || regpass.length < 5) {
        bootbox.alert({title: 'error', message: "<5"});
        return false;
    } else {
        param = "username=" + regname;
        param += "&password=" + regpass;
        param += '&ecode=' + regcode;
        $.post('/user', param, function (data) {
            if (data == "ecode-error") {
                bootbox.alert({title: '错误提示', message: '验证码无效'});
                $("#regcode").val("");
                $("#regcode").focus();
            } else if (data == "up-invalid") {
                bootbox.alert({title: '错误提示', message: '用户名和密码不能小于5位'});
            } else if (data == 'reg-pass') {
                bootbox.alert({title: "消息提示", message: '注册成功'});
            } else if (data == 'user-repeated') {
                bootbox.alert({title: "消息提示", message: "该账户已被注册"})
            }

        })

    }
}


function doLogin(e) {
    if (e != null && e.keyCode != 13) {
        return false;
    }
    var loginname = $.trim($("#loginname").val());
    var loginpass = $.trim($("#loginpass").val());
    var logincode = $.trim($("#logincode").val());

    if (!loginname.match(/.+@.+\..+/) || loginpass.length < 5) {
        bootbox.alert({title: 'error', message: "<5"});
        return false;
    } else {
        var param = "username=" + loginname;
        param += "&password=" + loginpass;
        param += '&vcode=' + logincode;
        $.post('/login', param, function (data) {
            if (data == "vcode-error") {
                bootbox.alert({title: '错误提示', message: '验证码无效'});
                $("#logincode").val("");
                $("#logincode").focus();
            }
            else if (data == 'login-pass') {
                    bootbox.alert({title: "消息提示", message: '登陆成功'});
                    setTimeout('location:reload();', 1000);
                }
            else if (data == 'login-fail') {
                    bootbox.alert({title: "消息提示", message: "登录失败"})
                }
            })/**/

        }
    }