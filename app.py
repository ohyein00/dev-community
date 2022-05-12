import codecs
import re
import gridfs

import jwt
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from bson import ObjectId
from werkzeug.utils import secure_filename

from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import dateutil.parser
import certifi

ca = certifi.where()
client = MongoClient('3.34.47.86', 27017, username="test", password="test")
db = client.dbsparta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"
app.secret_key = 'SPARTA'

SECRET_KEY = 'SPARTA'
fs = gridfs.GridFS(db)


def get_img_file(img_id):
    img_binary = fs.get(img_id)
    base64_img = codecs.encode(img_binary.read(), 'base64')
    decoded_img = base64_img.decode('utf-8')
    return decoded_img


# 유저 아이디 체크. 비로그인시 False값 출력
def check_user_id():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return payload["id"]
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return False


# 시간차 계산
def time_difference(compare_time):
    thisTime = datetime.now(timezone.utc)
    postTime = dateutil.parser.parse(compare_time)
    restTime = thisTime - postTime
    if restTime.days > 0:
        return str(restTime.days) + '일'  # 일
    elif int(restTime.seconds / 3600) > 0:
        return str(int(restTime.seconds / 3600)) + '시간'  # 시간
    elif int(restTime.seconds / 60) > 5:
        return str(int(restTime.seconds / 60)) + '분'  # 분
    else:
        return '방금'


# 문자열 자르기
def cut_string(string, max):
    if len(string) > max:
        result = string[0:max]
        return result


@app.route('/')
def main():
    # 메인에서 바로 피드 출력

    count_receive = request.cookies.get('count')
    count = 10
    if count_receive is not None:
        count = int(count_receive)
    posts = list(db.post_data.find({}).sort("date", -1).limit(count))
    user_id = check_user_id()
    comment_count = 0
    for post in posts:
        post["_id"] = str(post["_id"])
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"]})
        post["time_difference"] = time_difference(post["date"])
        image = []
        if len(post['img_ids']) > 0:
            for img_id in post['img_ids']:
                image.append(get_img_file(ObjectId(img_id)))

        post["cut_text"] = cut_string(post["text"], 200)
        post["s3_image_list"] = image
        post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
        post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}).sort("date", -1))
        for comment in post["comment_list"]:
            comment["_id"] = str(comment["_id"])
            comment["time_difference"] = time_difference(comment["date"])
        # 좋아요 유저체크 분기
        if bool(user_id):
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "username": user_id}))
        else:
            post["heart_by_me"] = False

    return render_template('index.html', posts=posts, user_id=user_id, comment_count=comment_count)


@app.route('/get_more_txt', methods=['GET'])
def get_more_txt():
    postId = request.args.get("id")
    post = db.post_data.find_one({"_id": ObjectId(postId)})
    return jsonify({'data': post["text"]})


@app.route('/write')
def write():
    btn_name = '게시'
    text = ''
    imgs = []
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        if len(request.args) > 0:
            btn_name = '수정 완료'
            post_id = request.args['post_id']
            post = db.post_data.find_one({'_id': ObjectId(post_id)})
            text = post['text']

            if len(post['img_ids']) > 0:
                for img_id in post['img_ids']:
                    imgs.append(get_img_file(ObjectId(img_id)))

        return render_template("write.html",
                               btn_name=btn_name,
                               nickname=user_info['nickname'],
                               text=text,
                               imgs=imgs)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("main"))

@app.route('/get_images', methods=['GET'])
def get_images():
    images = []
    post_id = request.args.get('post_id')
    post = db.post_data.find_one({'_id': ObjectId(post_id)})
    if len(post['img_ids']) > 0:
        for img_id in post['img_ids']:
            images.append(get_img_file(ObjectId(img_id)))

    return jsonify({'images': images})


@app.route('/list')
def lists():
    return render_template("list.html")


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        session['username'] = username_receive
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    name_receive = request.form['name_give']
    nickname_receive = request.form['nickname_give']

    doc = {
        "username": username_receive,
        "password": password_hash,
        "name": name_receive,
        "nickname": nickname_receive,
        "img": "profile_pics/profile_placeholder.png",
        "text": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup_username', methods=['POST'])
def check_dup_username():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_dup_nickname', methods=['POST'])
def check_dup_nickname():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/like_list')
def like_list():
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        user_id = check_user_id()
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            like_list = list(db.likes.find({"username": payload["id"]}).sort("_id", -1).limit(10))
            posts = list();
            for like in like_list:
                temp = db.post_data.find_one({"_id": ObjectId(like["post_id"])})
                if temp is not None:
                    posts.append(temp)
            # posts = list(db.post_data.find({ "$or": [{"_id":"627a7d829f7832603689b329"},{"_id":"627a8114ada74ce8b7468720"},{"_id":"627b06ca1d2c7f973e5b4d5f"}]}).sort("date", -1).skip(count).limit(3))
            posts_like = list()
            for post in posts:
                post["_id"] = str(post["_id"])
                post["count_heart"] = db.likes.count_documents({"post_id": post["_id"]})
                post["time_difference"] = time_difference(post["date"])
                image = []
                if len(post['img_ids']) > 0:
                    for img_id in post['img_ids']:
                        image.append(get_img_file(ObjectId(img_id)))

                post["cut_text"] = cut_string(post["text"], 200)
                post["s3_image_list"] = image
                post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
                post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}).sort("date", -1))
                for comment in post["comment_list"]:
                    comment["_id"] = str(comment["_id"])
                    comment["time_difference"] = time_difference(comment["date"])
                # 좋아요 유저체크 분기
                if bool(user_id):
                    post["heart_by_me"] = bool(
                        db.likes.find_one({"post_id": post["_id"], "username": user_id}))
                else:
                    post["heart_by_me"] = False
                posts_like.append(post)

            return render_template("like_list.html", posts=posts_like, user_id=user_id)
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect("/")
    else:
        return redirect(url_for("/"))

@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/post_content')
def post_content():
    return render_template("post_content.html")


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        text_receive = request.form['text']
        date_receive = request.form['date']
        option_receive = request.form['option']
        post_id_receive = request.form['post_id']

        pattern = '#([0-9a-zA-Z가-힣]*)'
        find_hash = re.compile(pattern)
        hash_tags = find_hash.findall(text_receive)
        text_receive = find_hash.sub("", text_receive)
        img_ids = []
        if request.files is not None:
            for file in request.files:
                img_id = fs.put(request.files[file])
                img_ids.append(str(img_id))

        if option_receive == 'update':
            post = db.post_data.find_one({'_id': ObjectId(post_id_receive)})
            if (len(post['img_ids']) > 0):
                for file_id in post['img_ids']:
                    obj_id = ObjectId(file_id)
                    db.fs.chunks.delete_one({'files_id': obj_id})
                    db.fs.files.delete_one({'_id': obj_id})
            db.post_data.update_one({'_id': ObjectId(post_id_receive)},
                                    {'$set': {'text': text_receive,
                                              'img_ids': img_ids,
                                              'hash_tags': hash_tags}})
        else:
            db.post_data.insert_one({
                "username": user_info['username'],
                "profile_name": user_info["nickname"],
                "profile_placeholder": user_info["img"],
                'date': date_receive,
                'text': text_receive,
                'hash_tags': hash_tags,
                'img_ids': img_ids
            })

        # hash_tag db
        for hash in hash_tags:
            if db.users.find_one({"username": user_info['username'], "hash_tags": hash}) is None:
                db.users.update_one({"username": user_info['username']}, {"$push": {"hash_tags": hash}})

        # if db.hash_folder.find_one({"username":user_info['username']}) is None:
        #     db.hash_folder.insert_one({"username":user_info['username']})
        # for hash in hash_tags:
        #     if db.hash_folder.find_one({"username":user_info['username'], "hash_tags":hash}) is None:
        #         db.hash_folder.update_one({"username":user_info['username']}, {"$push":{"hash_tags":hash}})

        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/comment_list', methods=['POST'])
def comment_list():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        doc = {
            "post_id": post_id_receive,
            "comment": comment_receive,
            "date": date_receive,
            "username": user_info["username"],
            "profile_name": user_info["nickname"]
        }
        db.comment.insert_one(doc)
        return jsonify({"result": "success", 'msg': '댓글 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=['GET'])
def get_posts():
    count = int(request.args.get("count"))
    token_receive = request.cookies.get('mytoken')
    sort_option = request.args['sortOption']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        if sort_option == 'old':
            posts = list(db.post_data.find({}).sort("date", 1).skip(count).limit(3))
        else:
            posts = list(db.post_data.find({}).sort("date", -1).skip(count).limit(3))
        # posts = list(db.post_data.find({}).sort("date", -1).skip(count).limit(3))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"]})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "username": payload["id"]}))

            image = []
            if len(post['img_ids']) > 0:
                for img_id in post['img_ids']:
                    image.append(get_img_file(ObjectId(img_id)))
            post["s3_image_list"] = image
            post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
            post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
            for comment in post["comment_list"]:
                comment["_id"] = str(comment["_id"])

        if sort_option == 'like':
            posts = sorted(posts, key=lambda post: -post['count_heart'])
        # 포스팅 목록 받아오기

        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts, "session": session["username"]})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts_like", methods=['GET'])
def get_posts_like():
    count = int(request.args.get("count"))
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        like_list = list(db.likes.find({"username": payload["id"]}).sort("_id", -1).skip(count).limit(3))
        posts = list();
        for like in like_list:
            temp = db.post_data.find_one({"_id": ObjectId(like["post_id"])})
            if temp is not None:
                posts.append(temp)
        # posts = list(db.post_data.find({ "$or": [{"_id":"627a7d829f7832603689b329"},{"_id":"627a8114ada74ce8b7468720"},{"_id":"627b06ca1d2c7f973e5b4d5f"}]}).sort("date", -1).skip(count).limit(3))
        posts_like = list()
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"]})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "username": payload["id"]}))
            if (post["heart_by_me"]):
                image = []
                if len(post['img_ids']) > 0:
                    for img_id in post['img_ids']:
                        image.append(get_img_file(ObjectId(img_id)))
                post["s3_image_list"] = image
                post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
                post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
                for comment in post["comment_list"]:
                    comment["_id"] = str(comment["_id"])
                posts_like.append(post)
        # 포스팅 목록 받아오기
        return jsonify(
            {"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts_like, "session": session["username"]})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_guest_posts", methods=['GET'])
def get_guest_posts():
    count = int(request.args.get("count"))
    posts = list(db.post_data.find({}).sort("date", -1).skip(count).limit(3))

    for post in posts:
        post["_id"] = str(post["_id"])
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
        post["heart_by_me"] = bool(
            db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": "GUEST"}))

        image = []
        if len(post['img_ids']) > 0:
            for img_id in post['img_ids']:
                image.append(get_img_file(ObjectId(img_id)))
        post["s3_image_list"] = image
        post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
        post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
        for comment in post["comment_list"]:
            comment["_id"] = str(comment["_id"])
    # 포스팅 목록 받아오기
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})


@app.route('/update_like', methods=['POST'])
def update_like():
    # 좋아요 수 변경

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})

        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/search", methods=['GET'])
def search():
    hash_receive = request.args.get("hash_give")
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.post_data.find({"hash_tags": hash_receive}).sort("date", -1).limit(20))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload["id"]}))

            image = []
            if len(post['img_ids']) > 0:
                for img_id in post['img_ids']:
                    image.append(get_img_file(ObjectId(img_id)))
            post["s3_image_list"] = image
            post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
            post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
            for comment in post["comment_list"]:
                comment["_id"] = str(comment["_id"])
        # 포스팅 목록 받아오기
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts, "session": session["username"]})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/guest_search", methods=['GET'])
def guest_search():
    hash_receive = request.args.get("hash_give")
    posts = list(db.post_data.find({"hash_tags": hash_receive}).sort("date", -1).limit(20))
    for post in posts:
        post["_id"] = str(post["_id"])
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
        post["heart_by_me"] = bool(
            db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": "GUEST"}))
        img_ids = post['img_ids']
        image = []
        if len(img_ids) > 0:
            for img_id in img_ids:
                image.append(get_img_file(ObjectId(img_id)))
        post["s3_image_list"] = image
        post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
        post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
        for comment in post["comment_list"]:
            comment["_id"] = str(comment["_id"])
    # 포스팅 목록 받아오기
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts, "session": session["username"]})


@app.route('/post/hash', methods=['GET'])
def post_hash():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        hash_tags = db.users.find_one({"username": user_info['username']})['hash_tags']
        return jsonify({"result": "success", "msg": "해쉬태그를 가져왔습니다.", "hash_tags": hash_tags})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/post/profile", methods=['GET'])
def post_by_hash():
    hash_receive = request.args.get("hash_give")
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        posts = list(
            db.post_data.find({"hash_tags": hash_receive, "username": user_info['username']}).sort("date", -1).limit(
                20))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload["id"]}))

            image = []
            if len(post['img_ids']) > 0:
                for img_id in post['img_ids']:
                    image.append(get_img_file(ObjectId(img_id)))
            post["s3_image_list"] = image
            post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
            post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
            for comment in post["comment_list"]:
                comment["_id"] = str(comment["_id"])
        # 포스팅 목록 받아오기
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/sort", methods=['GET'])
def sort():
    token_receive = request.cookies.get('mytoken')
    sort_option = request.args['opt']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        if sort_option == 'old':
            posts = list(db.post_data.find({}).sort("date", 1))
        else:
            posts = list(db.post_data.find({}).sort("date", -1))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"]})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "username": payload["id"]}))

            image = []
            if len(post['img_ids']) > 0:
                for img_id in post['img_ids']:
                    image.append(get_img_file(ObjectId(img_id)))
            post["s3_image_list"] = image
            post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
            post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
            for comment in post["comment_list"]:
                comment["_id"] = str(comment["_id"])

        if sort_option == 'like':
            posts = sorted(posts, key=lambda post: -post['count_heart'])
        # 포스팅 목록 받아오기
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/guest_sort", methods=['GET'])
def guest_sort():
    posts = list(db.post_data.find({}).sort("date", -1))
    sort_option = request.args['opt']

    if sort_option == 'old':
        posts = list(db.post_data.find({}).sort("date", 1))
    else:
        posts = list(db.post_data.find({}).sort("date", -1))

    for post in posts:
        post["_id"] = str(post["_id"])
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
        post["heart_by_me"] = bool(
            db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": "GUEST"}))

        image = []
        if len(post['img_ids']) > 0:
            for img_id in post['img_ids']:
                image.append(get_img_file(ObjectId(img_id)))
        post["s3_image_list"] = image
        post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
        post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
        for comment in post["comment_list"]:
            comment["_id"] = str(comment["_id"])

    if sort_option == 'like':
        posts = sorted(posts, key=lambda post: -post['count_heart'])
    # 포스팅 목록 받아오기
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})


@app.route("/post_delete", methods=['POST'])
def post_delete():
    post_id = request.form['post_id']
    print(post_id)
    db.post_data.delete_one({'_id': ObjectId(post_id)})
    return jsonify({"result": "success"})


@app.route("/comment_delete", methods=['POST'])
def comment_delete():
    comment_id = request.form['comment_id']
    print(comment_id)
    db.comment.delete_one({'_id': ObjectId(comment_id)})
    return jsonify({"result": "success"})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
