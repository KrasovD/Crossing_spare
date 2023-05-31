$(document).ready(function () {
    function auth_login(){
        var login = $('#login').val();
        var password = $('#password').val();

        if (login != "" && password != "") {
            $.ajax({
                method: "POST",
                url: '/login',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({ 'login': login, 'password': password }),
                dataType: "json",
                success: function () {
                    window.location.href = '/'
                },
                error: function () {
                    $('#error').html('Неверный логин или пароль');
                }
            });
        }
    }

    function auth_signup(){
        var login = $('#reglogin').val();
        var password = $('#regpassword').val();
        var key = $('#regkey').val();

        if (login != "" && password != "") {
            $.ajax({
                method: "POST",
                url: '/signup',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({ 'login': login, 'password': password, 'key': key }),
                dataType: "json",
                success: function (data) {
                    if (data['message'] == 'Успешно'){
                        $('#signupModal').modal('hide');
                        $('#LoginModal').modal('show');
                    } else{
                        $('#signupError').html(data['message']);
                    }
                },
            });
        }
    }

    function search_ditails() {
        var search = $('#search').val()
        var page = window.location.pathname
        if (search != '') {

            $.ajax({
                method: "GET",
                url: '/search',
                xhrFields: {
                    withCredentials: true
                },

                contentType: 'application/json;charset=UTF-8',
                data: { 'search': search },
                dataType: "json",
                beforeSend: function () {
                    $('#preloader-5').show();
                },
                success: function (data) {
                    $('#main').html(data['data']);
                    if (data['data'] != '\n      ') {
                        $('#spare').show();
                    }
                },
                complete: function () {
                    $('#preloader-5').hide();
                }
            });
        }
    }

    function parsing_details(){
        var search = $('#search').val()
        console.log(search)
        if (search != '') {
            $.ajax({
                method: "POST",
                url: '/scrape',
                xhrFields: {
                    withCredentials: true
                },

                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({ 'search': search }),
                dataType: "json",
                beforeSend: function () {
                    $('#preloader-5').show();
                },
                success: function (data) {
                    $('#main').html(data['data']);
                    if (data['data'] != '\n      ') {
                        $('#spare').show();
                    }
                },
                complete: function () {
                    $('#preloader-5').hide();
                }
            });
        }
    }


    $('#loginSubmit').on('click', function (e) {
        auth_login();
    });

    $('#signupSubmit').on('click', function (e) {
        auth_signup();
    });

    $('#password').keypress(function (e) {
        var key = e.which;
        if (key == 13)  // the enter key code
        {
            auth_login();
        };
    });

    $('#regpassword').keypress(function (e) {
        var key = e.which;
        if (key == 13)  // the enter key code
        {
            auth_signup();
        };
    });

    $('#btn_parsing').click(function (e) { 
        parsing_details();
    });

    $('#search').keypress(function (e) {
        var key = e.which;
        if (key == 13)  // the enter key code
        {
            parsing_details();
        }
    });

    $('#update_bd').on('click', function() {
        var values = [];
        $.each($("input:checked"), function(){
            var str = [$(this).attr('store'), $(this).val()];
            values.push(str);
        });

        $.ajax({
            type: "post",
            url: "/database",
            data: JSON.stringify(values),
            contentType: "application/json;charset=UTF-8",
            dataType: "json",
            success: function (response) {
                if (response['data'] == false){
                    alert('Идет загрузка')
                }
                else{
                    window.location.href = '/database'
                }
            }
        });
    });
    
    

});