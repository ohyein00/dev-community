$(function () {
    $('#new').click(function () {
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
    let token = $.cookie('mytoken');
    if (token !== undefined) {
        $(".login > small").text("로그아웃");
        $('.login').prop('href', 'javascript:void(0)')
        $('.login').attr('onclick', 'sign_out()')
    } else {
        $(".login > small").text("로그인");
        $('.login').prop('href', "/login")
        $('.login').removeAttr('onclick')
    }

})
const more_text = (event, postId) => {
    console.log(event.target)
    $.ajax({
        type: "GET",
        url: "/get_more_txt",
        data: {
            id: postId
        },
        success: function (response) {
            $(event.target).siblings('span.txt').text(response.data)
            $(event.target).hide()
        }
    })

}

const sortFeed = opt => {
    const feeds = document.getElementsByClassName('feed_frame');

    const getDataObj = iter => _.go(
        iter,
        L.map(v => v.dataset.postinfo),
        L.map(v => v.replace(/\'/g, '\"')),
        L.map(v => v.replace(/F/g, 'f')),
        _.map(v => JSON.parse(v))
    );

    const sortDataObj = _.curry((opt, iter) => _.go(
        iter,
        opt == "new"
            ? _.sortBy(v => _.go(
                v,
                getDataObj,
                _.map(v => v['date']))):
            opt == "old"
                ? _.sortByDesc(v => _.go(
                    v,
                    getDataObj,
                    _.map(v => v['date']))):
                _.sortBy(v => _.go(
                    v,
                    getDataObj,
                    _.map(v => v['count_heart'])))
    ));

    const elements = _.go(
        feeds,
        sortDataObj(opt)
    )

    $('#post-box').html('');
    for (const el of elements) {
        console.log(el);
        $('#post-box').append(el);
    }
}

const sort = opt => {
    let host_url = "";
    let token = $.cookie('mytoken');
    if (token !== undefined) {
        host_url = "sort";
    } else {
        host_url = "guest_sort";
    }

    $.ajax({
        type: "GET",
        url: `/${host_url}`,

        async: false,
        data: {opt: opt},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"]
                let elements = ``;
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i]
                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o"
                    let image_list = post["s3_image_list"];
                    let comment_list = post["comment_list"];
                    let hash_list = post['hash_tags']
                    let image_temp = ``;
                    let comment_temp = ``;
                    let hash_temp = ``;
                    const postId = post['_id'];

                    for (const file of image_list) {
                        let temp = `<div class="img_frame">
                                            <img src="data:image;base64, ${file}"/></li>
                                        </div>`;
                        image_temp = image_temp + temp;

                    }
                    for (let j = 0; j < comment_list.length; j++) {
                        let time_post = new Date(comment_list[j]["date"])
                        let time_before = time2str(time_post)
                        let temp = `<div class="comment_frame" id="${comment_list[j]["_id"]}">
                                        <figure class="user_img">
                                            <img src="https://bulma.io/images/placeholders/128x128.png" alt="Image">
                                        </figure>
                                        <div class="comment_detail">
                                            <p class="user_name">
                                                <strong>${comment_list[j]['profile_name']}</strong> 
                                                <small style="font-size: xx-small">@${comment_list[j]['username']}</small>
                                                <small class="time contour left">${time_before}</small>
                                            </p>
                                            <p class="user_comment">${comment_list[j]['comment']}</p>
                                        </div>
                                    </div>`

                        comment_temp = comment_temp + temp;
                    }
                    for (let j = 0; j < hash_list.length; j++) {
                        let temp = `<div class="hash_item">
                                            <a><small >#${hash_list[j]}</small></a>
                                        </div>`;
                        hash_temp = hash_temp + temp;
                    }
                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)
                    let html_temp = `<div class="feed_frame" id="${post['_id']}">
                            <article class="feed">
                                <div class="media user_info">
                                    <figure class="image user_img">
                                        <img src="/static/${post['profile_placeholder']}" alt="Image">
                                    </figure>
                                    <div class="text_area">
                                        <p class="user_name">
                                            <strong>${post['profile_name']}</strong> 
                                            <small style="font-size: xx-small">@${post['username']}</small>
                                        </p>
                                        <p class="feed_info">
                                            <span class="time">${time_before}</span>
                                            <span class="like_count left contour">좋아요 ${num2str(post['count_heart'])}</span>
                                            ${post['username'] == USER_NAME
                        ? `<span class="info_unit contour"><a href="/write?post_id=${postId}">수정</a></span>
                                                   <span onclick="postDelete('${postId}')" class="info_unit contour post_delete">삭제</span>`
                        : ``}
                                        </p>

                                    </div>
                                </div>
                                <div class="like_btn_area">
                                    <a class="level-item is-sparta like_btn" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                        <strong class="is-sparta">
                                            <i style="color:crimson" class="fa ${class_heart}"
                                               aria-hidden="true"></i></strong>
                                    </a>
                                </div>
                                <div class="feed_detail">
                                    <p class="detail has_more">
                                        <span class="txt">${post["text"]}</span>
                                        <button class="more_btn">
                                            더보기
                                        </button>
                                    </p>

                                    <div class="img_group" onclick="imageModal(this)">
                                        ${image_temp}                             
                                    </div>
                                    <div class="hash_group is_flex">
                                        ${hash_temp}                             
                                    </div>
                                </div>
                            </article>
                            <div class="feed_comment">
                                <div class="comment_group">
                                    ${comment_temp}
                                </div>
                                <div class="input_wrap">
                                    <div class="input_area gray_type is_flex">
                                        <label class="${post['_id']}">
                                            <input type="text" placeholder="댓글을 입력하세요" maxlength="100">
                                        </label>
                                        <button type="submit" onclick="comment('${post['_id']}')">
                                            입력
                                        </button>
                                    </div>
                                    
                                </div>
                            </div>
                        </div>`
                    elements += html_temp;

                }
                $('#post-box').html(elements);
            }

        }

    })
}

const postDelete = id => {

    if(confirm('삭제하시겠습니까?'))
        $.ajax({
            type: 'POST',
            url: '/post_delete',
            data: {post_id: id},
            success: function (res) {
                location.href = "/";
            }
        })
}

const imageModal = target => {
    const imgSwiper = new Swiper('.swiper', {
        grabCursor: true,
        autoHeight: true,
        centeredSlides: true,
    });

    $('#img_swiper_container').html('');
    $('#img_modal_wrap').removeClass('hidden');
    for (const img of $(target).find('img')) {
        const tmp  =  new Image();
        tmp.src = img.src;
        const div = document.createElement("div");
        tmp.className = "slide-img max-w-[80%]";
        div.className = "swiper-slide flex justify-center";
        div.appendChild(tmp);
        $('#img_swiper_container').append(div);
    }
}

const commentDelete = id => {
    $.ajax({
        type: 'POST',
        url: '/comment_delete',
        data: {comment_id: id},
        success: function (res) {
            window.location.reload();
        }
    })
}

function sign_out() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!')
    window.location.href = "/"


}