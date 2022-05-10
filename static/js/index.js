$(function () {
    console.log('hello')
    show_list()
})

function show_list() {
    $.ajax({
        type: 'GET',
        url: '/list',
        data: {},
        success: function (response) {
            console.log(response)
        }
    })
}