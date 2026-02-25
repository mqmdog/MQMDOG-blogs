/**
 * 注册页 - 邮箱验证码发送逻辑
 */
$(function () {
    var COUNTDOWN_SECONDS = 60;

    function bindCaptchaBtnClick() {
        $('#captcha-btn').click(function () {
            var $btn = $(this);
            var email = $("input[name='email']").val();

            if (!email || !email.trim()) {
                alert('请先输入邮箱！');
                return;
            }

            // 禁用按钮防止重复点击
            $btn.prop('disabled', true);

            // 发送验证码请求
            $.ajax({
                url: '/auth/captcha?email=' + encodeURIComponent(email),
                method: 'GET',
                success: function (result) {
                    if (result['code'] === 200) {
                        alert('验证码发送成功！');
                    } else {
                        alert(result['message'] || '发送失败');
                    }
                },
                error: function () {
                    alert('网络错误，请重试！');
                },
            });

            // 倒计时
            var countdown = COUNTDOWN_SECONDS;
            var timer = setInterval(function () {
                if (countdown <= 0) {
                    clearInterval(timer);
                    $btn.text('获取验证码').prop('disabled', false);
                } else {
                    countdown--;
                    $btn.text(countdown + 's');
                }
            }, 1000);
        });
    }

    bindCaptchaBtnClick();
});
