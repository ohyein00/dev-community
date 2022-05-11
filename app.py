import codecs
import re
import gridfs

import jwt
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from bson import ObjectId
from werkzeug.utils import secure_filename

from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi

ca = certifi.where()
client = MongoClient('3.34.47.86', 27017, username="test", password="test")
db = client.dbsparta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'
fs = gridfs.GridFS(db)

def get_img_file(img_id):
    img_binary = fs.get(img_id)
    base64_img = codecs.encode(img_binary.read(), 'base64')
    decoded_img = base64_img.decode('utf-8')
    return decoded_img


@app.route('/')
def main():
    myname = "Devom"
    return render_template("index.html", name=myname)

@app.route('/write')
def write():
    return render_template("write.html")
@app.route('/list')
def lists():
    return render_template("list.html")

@app.route('/read', methods=['GET'])
def read():
    return render_template("read.html")

@app.route('/read_result', methods=['GET'])
def read_result():
    contents = list(db.tmp.find({}))
    result = []
    for content in contents:
        img_ids = content['img_ids']
        results = []
        if len(img_ids) > 0:
            for img_id in img_ids:
                results.append(get_img_file(img_id))
        result.append(results)

    return jsonify({'result': 'success', 'files': result})

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
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
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
    return render_template("like_list.html")


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

        pattern = '#([0-9a-zA-Z가-힣]*)'
        find_hash = re.compile(pattern)
        hash_tags = find_hash.findall(text_receive)
        text_receive =find_hash.sub("", text_receive)
        img_ids = []
        if request.files is not None:
            for file in request.files:
                img_id = fs.put(request.files[file])
                img_ids.append(str(img_id))

        db.post_data.insert_one({
            "username": user_info['username'],
            "profile_name": user_info["nickname"],
            "profile_placeholder": user_info["img"],
            'date': date_receive,
            'text': text_receive,
            'hash_tags': hash_tags,
            'img_ids': img_ids
        })

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
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.post_data.find({}).sort("date", -1).limit(20))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload["id"]}))

            image = []
            if len(post['img_ids']) > 0:
                for img_id in post['img_ids']:
                    image.append(get_img_file(ObjectId(img_id)))
            post["s3_image_list"] =image
            post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
            post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
            for comment in post["comment_list"]:
                comment["_id"] = str(comment["_id"])
        # 포스팅 목록 받아오기
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_guest_posts", methods=['GET'])
def get_guest_posts():
    posts = list(db.post_data.find({}).sort("date", -1).limit(20))
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
        print(count)
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/search", methods=['GET'])
def search():
    hash_receive = request.args.get("hash_give")
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.post_data.find({"hash_tags":hash_receive}).sort("date", -1).limit(20))

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
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})

@app.route('/logout', methods=['GET'])
def logout():
    return redirect("/")



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
