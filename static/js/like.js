function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return "0"
    }
    return count
}

function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

function comment(id) {
    let comment = $(`.${id} input`).val();
    let today = new Date().toISOString()
    $.ajax({
        type: "POST",
        url: "/comment_list",
        data: {
            post_id_give: id,
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            window.location.reload()
        }
    })
}

function toggle_comment() {

    if ($(".comment_frame:nth-of-type(n+4)").css('display') === 'flex') {
        $(".comment_frame:nth-of-type(n+4)").css('display', 'none');
    } else {
        $(".comment_frame:nth-of-type(n+4)").css('display', 'flex');
    }

}

function get_posts(count, sortOption = "new") {

    let posts_list = new Array();
    let host_url = "";
    let token = $.cookie('mytoken');

    $.cookie('count', count, {path: '/'});

    if (token !== undefined) {
        host_url = "get_posts";
    } else {
        host_url = "get_guest_posts";
    }
    $.ajax({
        type: "GET",
        url: `/${host_url}`,

        async: false,
        data: {
            count: count,
            sortOption: sortOption
        },
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"]
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
                          console.log(response["session"],comment_list[j]['username'])
                        let temp = `<div class="comment_frame" id="${comment_list[j]["_id"]}">
                                        <figure class="user_img">
                                            <img src="https://bulma.io/images/placeholders/128x128.png" alt="Image">
                                        </figure>
                                        <div class="comment_detail">
                                            <p class="user_name">
                                                <strong>${comment_list[j]['profile_name']}</strong> 
                                                <small style="font-size: xx-small">@${comment_list[j]['username']}</small>
                                                <small class="time contour left">${time_before}</small>
                                                 ${response["session"] === comment_list[j]['username'] ?
                                                                `<small class="feed_info">
                                                                <span onclick="commentDelete('${comment_list[j]["_id"]}')"
                                                                          class="time contour deleter">| 삭제</span>
                                                                </small>` : ``}
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

                                    <div class="img_group">
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
                    if (post["count_comment"] > 3) {
                        html_temp = `<div class="feed_frame" id="${post['_id']}">
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

                                    <div class="img_group">
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
                                    <diV style="width: 100%; display: flex; align-items: center; justify-content: center;">
                                            <button style="border: 0px;"  class="more_btn" onclick="toggle_comment()">
                                                <img width="15" height="15" src="/static/profile_pics/more_icon.png">
                                            </button>
                                        </div>
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
                    }
                    posts_list.push(html_temp);

                }
            }
        }

    })
    return posts_list
}

function get_posts_like(count) {
    let posts_list = new Array();
    $.cookie('count', count, {path: '/'});
    $.ajax({
        type: "GET",
        url: `/get_posts_like`,
        async: false,
        data: {count: count},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"]
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i]
                    let class_heart = 'fa-heart-o'
                    class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o"
                    let image_list = post["s3_image_list"];
                    let comment_list = post["comment_list"];
                    let image_temp = ``;
                    let comment_temp = ``;
                    for (const file of image_list) {
                        let temp = `<div class="img_frame">
                                            <img src="data:image;base64, ${file}"/></li>
                                        </div>`;
                        image_temp = image_temp + temp;

                    }
                    for (let j = 0; j < comment_list.length; j++) {
                        let time_post = new Date(comment_list[j]["date"])
                        let time_before = time2str(time_post)
                        console.log(response["session"],comment_list[j]["_id"])
                        let temp = `<div class="comment_frame" id="${comment_list[j]["_id"]}">
                                        <figure class="user_img">
                                            <img src="https://bulma.io/images/placeholders/128x128.png" alt="Image">
                                        </figure>
                                        <div class="comment_detail">
                                            <p class="user_name">
                                                <strong>${comment_list[j]['profile_name']}</strong> 
                                                <small style="font-size: xx-small">@${comment_list[j]['username']}</small>
                                                <small class="time contour left">${time_before}</small>
                                                ${response["session"] === comment_list[j]['username'] ?
                                                                `<small class="feed_info">
                                                                <span onclick="commentDelete('${comment_list[j]["_id"]}')"
                                                                          class="time contour deleter">| 삭제</span>
                                                                </small>` : ``}
                                            </p>
                                            <p class="user_comment">${comment_list[j]['comment']}</p>
                                        </div>
                                    </div>`

                        comment_temp = comment_temp + temp;
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
                                        </p>

                                    </div>
                                </div>
                                <div class="like_btn_area">
                                    <a class="level-item is-sparta like_btn" aria-label="heart" onclick="toggle_like_bookmark('${post['_id']}', 'heart')">
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

                                    <div class="img_group">
                                        ${image_temp}                             
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
                    posts_list.push(html_temp);
                }
            }
        }
    })
    return posts_list
}
function location_change(page){
    if (USER_NAME != "Guest"){
        $.cookie('count', 10, {path: '/'});
        window.location.href =page;
    }else {
        alert("로그인이 필요한 페이지 입니다.");
    }

}

function toggle_like(post_id, type) {
    let token = $.cookie('mytoken');

    if (token !== undefined) {
        let $a_like = $(`#${post_id} a[aria-label='heart']`)
        let $i_like = $a_like.find("i")
        if ($i_like.hasClass("fa-heart")) {
            $.ajax({
                type: "POST",
                url: "/update_like",
                data: {
                    post_id_give: post_id,
                    type_give: type,
                    action_give: "unlike"
                },
                success: function (response) {
                    $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                    $(`.feed_info > span:nth-child(2)`).text("좋아요 " + num2str(response["count"]))
                    $a_like.find("span.like_count").text(num2str(response["count"]))
                }
            })
        } else {
            $.ajax({
                type: "POST",
                url: "/update_like",
                data: {
                    post_id_give: post_id,
                    type_give: type,
                    action_give: "like"
                },
                success: function (response) {
                    $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                    $(`.feed_info > span:nth-child(2)`).text("좋아요 " + num2str(response["count"]))
                    console.log($(`#${post_id}`))
                    $a_like.find("span.like_count").text(num2str(response["count"]))
                }
            })

        }
    } else {
        alert("로그인 후에 사용하실 수 있습니다.")
    }
}

function toggle_like_bookmark(post_id, type) {
    let token = $.cookie('mytoken');
    if (token !== undefined) {
        let $a_like = $(`#${post_id} a[aria-label='heart']`)
        let $i_like = $a_like.find("i")
        if ($i_like.hasClass("fa-heart")) {
            $.ajax({
                type: "POST",
                url: "/update_like",
                data: {
                    post_id_give: post_id,
                    type_give: type,
                    action_give: "unlike"
                },
                success: function (response) {
                    $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                    $(`.feed_info > span:nth-child(2)`).text("좋아요 " + num2str(response["count"]))
                    $a_like.find("span.like_count").text(num2str(response["count"]))
                    window.location.reload()
                }
            })
        } else {
            $.ajax({
                type: "POST",
                url: "/update_like",
                data: {
                    post_id_give: post_id,
                    type_give: type,
                    action_give: "like"
                },
                success: function (response) {
                    $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                    $(`.feed_info > span:nth-child(2)`).text("좋아요 " + num2str(response["count"]))
                    console.log($(`#${post_id} .like_count`).text())
                    $a_like.find("span.like_count").text(num2str(response["count"]))
                }
            })

        }
    } else {
        alert("로그인 후에 사용하실 수 있습니다.")
    }
}
