function infinity_scroll_list(count) {

    window.onscroll = function (e) {
        //추가되는 임시 콘텐츠
        //window height + window scrollY 값이 document height보다 클 경우,
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight-10) {
            //실행할 로직 (콘텐츠 추가)

            let posts_lists = get_posts(count);
            if (posts_lists.length < 1) {
                return
            } else {
                count += 3;
                for (let i = 0; i < posts_lists.length; i++) {
                    $("#post-box").append(posts_lists[i])
                }
            }


        }
    };
}
function infinity_scroll_like(count) {
    window.onscroll = function (e) {
        //추가되는 임시 콘텐츠
        //window height + window scrollY 값이 document height보다 클 경우,
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
            //실행할 로직 (콘텐츠 추가)

            let posts_lists = get_posts_like(count);
            if (posts_lists.length >= 1) {
                 count += 3;
                for (let i = 0; i < posts_lists.length; i++) {
                    $("#post-box").append(posts_lists[i])
                }
            }
        }
    };
}
