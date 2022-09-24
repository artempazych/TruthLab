$(document).ready(
    function() {
        // Themes
        /*if (document.getElementById('theme-predict') == null)
            return;*/
        document.getElementById('theme-predict').addEventListener('submit', function (event) {
            event.preventDefault();
            document.getElementById('theme-predict-result').innerText = '';
            $.post('/theme/predict', {'text':  document.getElementById('theme-predict').text.value }, function (res) {
                document.getElementById('theme-predict-result').innerText = res.label;
            }, 'json');
        });
        document.getElementById('theme-add').addEventListener('submit', function (event) {
            event.preventDefault();
            $.post('/theme/add', {'name' : document.getElementById('theme-name').value , 'text':  document.getElementById('theme-text').value }, function (res) {
                if (res.status == 'OK')
                {
                    document.getElementById('theme-name').value = '';
                    document.getElementById('theme-text').value = '';
                }
                updateThemesList();
            }, 'json');
        });
        // Languages
        document.getElementById('language-predict').addEventListener('submit', function (event) {
            event.preventDefault();
            document.getElementById('language-predict-result').innerText = '';
            $.post('/language/predict', {'text':  document.getElementById('language-predict').text.value }, function (res) {
                document.getElementById('language-predict-result').innerText = res.label;
            }, 'json');
        });
        document.getElementById('language-add').addEventListener('submit', function (event) {
            event.preventDefault();
            $.post('/language/add', {'name' : document.getElementById('language-name').value , 'text':  document.getElementById('language-text').value }, function (res) {
                if (res.status == 'OK')
                {
                    document.getElementById('language-name').value = '';
                    document.getElementById('language-text').value = '';
                }
                updateLanguagesList();
            }, 'json');
        });
        // Spam
        document.getElementById('spam-predict').addEventListener('submit', function (event) {
            event.preventDefault();
            document.getElementById('spam-predict-result').innerText = '';
            $.post('/spam/predict', {'text':  document.getElementById('spam-predict').text.value }, function (res) {
                document.getElementById('spam-predict-result').innerText = res.label;
            }, 'json');
        });
        document.getElementById('spam-add').addEventListener('submit', function (event) {
            event.preventDefault();
            $.post('/spam/add', {'text':  document.getElementById('spam-text').value }, function (res) {
                if (res.status == 'OK')
                {
                    document.getElementById('spam-text').value = '';
                }
                updateSpamList();
            }, 'json');
        });
        // Fake
        document.getElementById('fake-predict').addEventListener('submit', function (event) {
            event.preventDefault();
            document.getElementById('fake-predict-result').innerText = '';
            $.post('/fake/predict', {'text':  document.getElementById('fake-predict').text.value }, function (res) {
                document.getElementById('fake-predict-result').innerText = res.label;
            }, 'json');
        });
        document.getElementById('fake-add').addEventListener('submit', function (event) {
            event.preventDefault();
            $.post('/fake/add', {'text':  document.getElementById('fake-text').value }, function (res) {
                if (res.status == 'OK')
                {
                    document.getElementById('fake-text').value = '';
                }
                updateFakeList();
            }, 'json');
        });
        // Complex Analisis
        document.getElementById('complex-predict').addEventListener('submit', function (event) {
            event.preventDefault();
            document.getElementById('complex-list').innerText = '';
            $.post('/complex/predict', {'text':  document.getElementById('complex-predict').text.value }, function (res) {
                document.getElementById('complex-list').innerHTML = res;
                document.getElementById('complex-analisis-button').dispatchEvent(new MouseEvent('click', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true
                }));
            }, 'html');
        });
        // Profile Edit
        document.getElementById('profile-edit').addEventListener('submit', function (event) {
            event.preventDefault();
            $.post('/user/profile', {'password1':  document.getElementById('profile-password-1').value, 'password2':  document.getElementById('profile-password-2').value, 'username':  document.getElementById('profile-username').value },
                function (res) {
                if (res.status == 'OK')
                {
                    UpdateProfile();
                }
            }, 'json');
        });
       /* document.getElementById('news-scraping').addEventListener('submit', function (event) {
            event.preventDefault();
            document.getElementById('news-scraping-status').innerText = '... здійснюється збір даних ...';
            $.post('/news/scraping', {'url':  document.getElementById('url').value, 'site' : $('#site').val() }, function (res) {
                document.getElementById('news-scraping-status').innerText = 'Зібрано ' + res.count + ' новин';
            }, 'json');
        });*/
        updateThemesList();
        updateLanguagesList();
        updateSpamList();
        updateFakeList();
        UpdateUsersList();
        // Themes
        $(document).on('click', 'a.theme-edit', function(event)
        {
            event.preventDefault();
             $.get(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    document.getElementById('themes-list').innerHTML = res;
             }, 'html');
        });
        $(document).on('click', 'button.theme-edit-cancel', function(event)
        {
            event.preventDefault();
            updateThemesList();
        });
        $(document).on('click', 'button.theme-edit-save', function(event)
        {
            event.preventDefault();
            console.log($(event.target).closest('form').attr('action'));
            $.post($(event.target).closest('form').attr('action'), {
                name : document.getElementById('theme-edit-name').value,
                text : document.getElementById('theme-edit-text').value
            }, function (res) {
                    updateThemesList();
                }, 'json');
        });
        // Languages
        $(document).on('click', 'a.language-edit', function(event)
        {
            event.preventDefault();
             $.get(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    document.getElementById('languages-list').innerHTML = res;
             }, 'html');
        });
        $(document).on('click', 'button.language-edit-cancel', function(event)
        {
            event.preventDefault();
            updateLanguagesList();
        });
        $(document).on('click', 'button.language-edit-save', function(event)
        {
            event.preventDefault();
            console.log($(event.target).closest('form').attr('action'));
            $.post($(event.target).closest('form').attr('action'), {
                name : document.getElementById('language-edit-name').value,
                text : document.getElementById('language-edit-text').value
            }, function (res) {
                    updateLanguagesList();
                }, 'json');
        });
        // Spam
        $(document).on('click', 'a.spam-edit', function(event)
        {
            event.preventDefault();
             $.get(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    document.getElementById('spam-list').innerHTML = res;
             }, 'html');
        });
        $(document).on('click', 'button.spam-edit-cancel', function(event)
        {
            event.preventDefault();
            updateSpamList();
        });
        $(document).on('click', 'button.spam-edit-save', function(event)
        {
            event.preventDefault();
            console.log($(event.target).closest('form').attr('action'));
            $.post($(event.target).closest('form').attr('action'), {
                text : document.getElementById('spam-edit-text').value
            }, function (res) {
                    updateSpamList();
                }, 'json');
        });
        // Fake
        $(document).on('click', 'a.fake-edit', function(event)
        {
            event.preventDefault();
             $.get(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    document.getElementById('fake-list').innerHTML = res;
             }, 'html');
        });
        $(document).on('click', 'button.fake-edit-cancel', function(event)
        {
            event.preventDefault();
            updateFakeList();
        });
        $(document).on('click', 'button.fake-edit-save', function(event)
        {
            event.preventDefault();
            console.log($(event.target).closest('form').attr('action'));
            $.post($(event.target).closest('form').attr('action'), {
                text : document.getElementById('fake-edit-text').value
            }, function (res) {
                    updateFakeList();
                }, 'json');
        });
        // Admin
        $(document).on('click', 'a.admin-fit-link', function(event)
        {
             document.getElementById('admin-fit-alert').style.display = 'none';
            event.preventDefault();
             $.get(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    document.getElementById('admin-fit-alert').innerHTML = res.status;
                    document.getElementById('admin-fit-alert').style.display = 'block';
             }, 'json');
        });

        $(document).on('click', 'a.user-edit', function(event)
        {
            event.preventDefault();
             $.get(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    document.getElementById('users-list').innerHTML = res;
             }, 'html');
        });
        $(document).on('click', 'button.user-edit-cancel', function(event)
        {
            event.preventDefault();
            UpdateUsersList();
        });
        $(document).on('click', 'button.user-edit-save', function(event)
        {
            event.preventDefault();
            $.post($(event.target).closest('form').attr('action'), {
                login : document.getElementById('profile-login').value,
                password : document.getElementById('user-edit-password').value,
                username : document.getElementById('user-edit-username').value,
                access : document.getElementById('user-edit-access').value
            }, function (res) {
                    UpdateUsersList();
                }, 'json');
        });
    });




function updateThemesList()
{
    $.post('/theme/getlist', {}, function (res) {
        document.getElementById('themes-list').innerHTML = res;
        $(document).on('click', 'a.theme-delete', function(event)
        {
            document.querySelector('#themes-list table').style.opacity = 0.5;
            event.preventDefault();
             $.post(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    updateThemesList();
                }, 'json');
        });

    }, 'html');
}
function updateLanguagesList()
{
    $.post('/language/getlist', {}, function (res) {
        document.getElementById('languages-list').innerHTML = res;
        $(document).on('click', 'a.language-delete', function(event)
        {
            document.querySelector('#languages-list table').style.opacity = 0.5;
            event.preventDefault();
             $.post(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    updateLanguagesList();
                }, 'json');
        });

    }, 'html');
}
function updateSpamList()
{
    $.post('/spam/getlist', {}, function (res) {
        document.getElementById('spam-list').innerHTML = res;
        $(document).on('click', 'a.spam-delete', function(event)
        {
            document.querySelector('#spam-list table').style.opacity = 0.5;
            event.preventDefault();
             $.post(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    updateSpamList();
                }, 'json');
        });

    }, 'html');
}
function updateFakeList()
{
    $.post('/fake/getlist', {}, function (res) {
        document.getElementById('fake-list').innerHTML = res;
        $(document).on('click', 'a.fake-delete', function(event)
        {
            document.querySelector('#fake-list table').style.opacity = 0.5;
            event.preventDefault();
             $.post(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    updateFakeList();
                }, 'json');
        });
    }, 'html');
}
function UpdateProfile()
{
     $.get('/user/profile', {}, function (res) {
        document.getElementById('user-profile').innerHTML = res;
    }, 'html');
}

function UpdateUsersList()
{
     $.get('/user/list', {}, function (res) {
        document.getElementById('users-list').innerHTML = res;
        $(document).on('click', 'a.user-delete', function(event)
        {
            document.querySelector('#users-list table').style.opacity = 0.5;
            event.preventDefault();
             $.post(event.target.closest('a').getAttribute('href'), {}, function (res) {
                    UpdateUsersList();
                }, 'json');
        });
    }, 'html');
}