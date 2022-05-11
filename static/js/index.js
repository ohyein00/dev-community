$(function () {
    $('#new').click(function() {
        $('.sort_item').removeClass('text_red');
        $('#old').addClass('text_red');
        $('#old').removeClass('sort_hidden');
        $('#new').addClass('sort_hidden');
    });
    $('#old').click(function () {
        $('.sort_item').removeClass('text_red');
        $('#new').addClass('text_red');
        $('#new').removeClass('sort_hidden');
        $('#old').addClass('sort_hidden');
    });
    $('#like').click(function () {
        $('.sort_item').removeClass('text_red');
        $('#like').addClass('text_red');
    });

})
const more_text = (event,postId) => {
    console.log(event.target)
    $.ajax({
        type: "GET",
        url: "/get_more_txt",
        data: {
            id:postId
        },
        success: function (response) {
            $(event.target).siblings('span.txt').text(response.data)
            $(event.target).hide()
        }
    })

}