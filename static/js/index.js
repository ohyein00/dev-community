$(function () {
    show_list()

    $('#new').click(function() {
        $('.sort_item').removeClass('text_red');
        $('#old').addClass('text_red');
        $('#old').removeClass('sort_hidden');
        $('#new').addClass('sort_hidden');
    });
    $('#old').click(function() {
        $('.sort_item').removeClass('text_red');
        $('#new').addClass('text_red');
        $('#new').removeClass('sort_hidden');
        $('#old').addClass('sort_hidden');
    });
    $('#like').click(function() {
        $('.sort_item').removeClass('text_red');
        $('#like').addClass('text_red');
    });
})

function show_list() {
    $.ajax({
        type: 'GET',
        url: '/list',
        data: {},
        success: function (response) {
        }
    })
}