/**
 * 博客发布页 - 富文本编辑器初始化及表单提交
 */
window.onload = function () {
    const { createEditor, createToolbar } = window.wangEditor;

    // 初始化富文本编辑器
    const editor = createEditor({
        selector: '#editor-container',
        html: '<p><br></p>',
        config: {
            placeholder: '请输入文章内容...',
        },
        mode: 'default',
    });

    createToolbar({
        editor,
        selector: '#toolbar-container',
        config: {},
        mode: 'default',
    });

    // 发布按钮点击事件
    $('#submit-btn').click(function (event) {
        event.preventDefault();

        var title = $("input[name='title']").val();
        var category = $("#category-select").val();
        var content = editor.getHtml();
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();

        if (!title || !title.trim()) {
            alert('请输入文章标题');
            return;
        }

        if (!content || content === '<p><br></p>') {
            alert('请输入文章内容');
            return;
        }

        $.ajax({
            url: '/pub/',
            method: 'POST',
            data: {
                title: title,
                category: category,
                content: content,
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (result) {
                if (result['code'] === '200') {
                    var blogId = result['data']['blog_id'];
                    window.location.href = '/blog/detail/' + blogId;
                } else {
                    alert('发布失败: ' + (result['msg'] || '未知错误'));
                }
            },
            error: function () {
                alert('网络错误，请稍后重试');
            },
        });
    });
};
