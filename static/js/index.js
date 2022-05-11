$(function () {
    show_list()

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