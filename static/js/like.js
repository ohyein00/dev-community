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
    let comment = $(`.${id} > input`).val();
    let today = new Date().toISOString()
    console.log(comment);
    $.ajax({
        type: "POST",
        url: "/comment_list",
        data: {
            post_id_give: id,
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active")
            window.location.reload()
        }
    })
}

function post() {
    let comment = $("#textarea-post").val()
    let today = new Date().toISOString()
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active")
            window.location.reload()
        }
    })
}

function toggle_comment(id) {
    let token = $.cookie('mytoken');
    if (token !== undefined) {
        if ($(`#${id} > .modal`).hasClass("is-active")) {
            $(`#${id} > .modal`).removeClass("is-active");
        } else {
            $(`#${id} > .modal`).addClass("is-active");
        }
    }else {
        alert("로그인 후에 사용하실 수 있습니다.")
    }


}

function get_posts() {
    $("#post-box").empty()
    let host_url = "";
    let token = $.cookie('mytoken');
    if (token !== undefined) {
        host_url = "get_posts";
    } else {
        host_url = "get_guest_posts";
    }

    $.ajax({
        type: "GET",
        url: `/${host_url}`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"]
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i]
                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o"
                    let image_list = post["s3_image_list"];
                    let comment_list = post["comment_list"];
                    let image_temp = ``;
                    let comment_temp = ``;
                    console.log(comment_list)
                    for (const file of image_list) {
                        let temp = `<li><img src="data:image;base64, ${file}"/></li>`;
                        image_temp = image_temp + temp;

                    }
                    for (let j = 0; j < comment_list.length; j++) {
                        let time_post = new Date(comment_list[j]["date"])
                        let time_before = time2str(time_post)
                        let temp = `<div class="box" id="${comment_list[j]["_id"]}">
                                                                    <article class="media">
                                                                        <div class="media-left">
                                                                            <a class="image is-64x64" href="/user/${comment_list[j]['username']}">
                                                                                <strong class="is-sparta"
                                                                            style="font-family: 'Stylish', sans-serif;font-size: xxx-large;"><i
                                                                            style="color:gray"
                                                                            class="fa fa-user"
                                                                            aria-hidden="true"></i></strong>
                                                                            </a>
                                                                        </div>
                                                                        <div class="media-content">
                                                                        <div>
                                                                            <div class="content">
                                                                                <p>
                                                                                    <strong>${comment_list[j]['profile_name']}</strong> <small>@${comment_list[j]['username']}</small> <small>${time_before}</small>
                                                                                    <br>
                                                                                    ${comment_list[j]['comment']}
                                                                                </p>

                                                                            </div>
                                                                        </div>
                                                                        </div>
                                                                    </article>
                                                                </div>`;
                        comment_temp = comment_temp + temp;
                    }
                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)
                    let html_temp = `<section class="box" id="${post["_id"]}">
                                        <article class="media">
                                            <div class="media-left">
                                                <a class="image is-64x64" href="/user/${post['username']}">
                                                    <strong class="is-sparta"
                                                style="font-family: 'Stylish', sans-serif;font-size: xxx-large;"><i
                                                style="color:gray"
                                                class="fa fa-user"
                                                aria-hidden="true"></i></strong>
                                                </a>
                                            </div>
                                            <div class="media-content">
                                                <div class="content">
                                                    <p>
                                                        <strong>${post['profile_name']}</strong> <small>@${post['username']}</small> <small>${time_before}</small>
                                                        <br>
                                                        ${post['text']}
                                                    </p>

                                                </div>
                                                <div class="image_list">
                                                    ${image_temp}
                                                </div>
                                                <nav class="level is-mobile">
                                                    <div class="level-right">
                                                        <a class="level-item is-sparta" aria-label="comment" onclick="toggle_comment('${post['_id']}')">
                                                            <span class="icon is-small"><i style="color: blue"  class="fa fa-comment" aria-hidden="true"></i></span>&nbsp;<span style="color: blue"  class="comment-num">${num2str(post['count_comment'])}</span>
                                                        </a>
                                                        <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                            <span class="icon is-small"><i class='fa ${class_heart}'
                                                                                           aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_heart'])}</span>
                                                        </a>
                                                    </div>
                                                </nav>

                                            </div>

                                        </article>
                                        <div class="modal" id="modal-comment">
                                             <div class="modal-background" onclick="toggle_comment('${post['_id']}')"></div>
                                                <div class="modal-content">
                                                    <div class="box">
                                                        ${comment_temp}
                                                        <article class="media">
                                                            <div class="media-content" style="display: flex; justify-content: center; align-items: center">
                                                                <div style=" margin:0px; width: 60%; padding: 0px" class="${post['_id']}" >
                                                                    <input style=" width: 100%; height:40px; border: 0px; box-shadow: 3px 3px 10px #ccc;"  type="text" placeholder="댓글">
                                                                </div>
                                                                <nav class="level is-mobile" >

                                                                    <div class="level-right">
                                                                        <div class="level-item">
                                                                            <a class="button is-sparta" onclick="comment('${post['_id']}')">댓글달기</a>
                                                                        </div>
                                                                        <div class="level-item">
                                                                            <a class="button is-sparta is-outlined"
                                                                               onclick="toggle_comment('${post['_id']}')">취소</a>
                                                                        </div>
                                                                    </div>
                                                                </nav>
                                                            </div>
                                                        </article>
                                                    </div>
                                                </div>

                                                <button class="modal-close is-large" aria-label="close"
                            onclick="toggle_comment('${post['_id']}')"></button>
                                        </div>
                                    </section>`
                    $("#post-box").append(html_temp)
                }
            }
        }
    })
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
                    console.log("unlike")
                    $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                    $a_like.find("span.like-num").text(num2str(response["count"]))
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
                    console.log("like")
                    $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                    $a_like.find("span.like-num").text(num2str(response["count"]))
                }
            })

        }
    } else {
        alert("로그인 후에 사용하실 수 있습니다.")
    }


}
