from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for
import boto3
from datetime import datetime

client = MongoClient('3.34.47.86', 27017, username="test", password="test")
db = client.devom

app = Flask(__name__)

ACCESS_KEY_ID = "AKIARGAT3YC473OUDAXX"
ACCESS_SECRET_KEY = "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"
BUCKET_NAME = "devom-image"


@app.route('/')
def main():
    myname = "Devom"
    return render_template("index.html", name=myname)


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
    user_info = db.users.find_one({"username": "test1"})
    comment_receive = request.form["comment_give"]
    date_receive = request.form["date_give"]
    doc = {
        "username": "test1",
        "profile_name": "test",
        "profile_pic_real": "yes",
        "comment": comment_receive,
        "date": date_receive
    }
    db.posts.insert_one(doc)
    return jsonify({"result": "success", 'msg': '포스팅 성공'})

@app.route('/comment_list', methods=['POST'])
def comment_list():
    user_info = db.users.find_one({"username": "test1"})
    post_id_receive = request.form["post_id_give"]
    comment_receive = request.form["comment_give"]
    date_receive = request.form["date_give"]
    doc = {
        "post_id": post_id_receive,
        "comment": comment_receive,
        "date": date_receive,
        "username":"test1"
    }
    db.comment.insert_one(doc)
    return jsonify({"result": "success", 'msg': '댓글 성공'})

@app.route("/get_posts", methods=['GET'])
def get_posts():
    posts = list(db.posts.find({}).sort("date", -1).limit(20))
    for post in posts:
        post["_id"] = str(post["_id"])
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
        post["heart_by_me"] = bool(
            db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": "test"}))
        post["s3_image_list"] = ["https://devom-image.s3.ap-northeast-2.amazonaws.com/img/test/01.jpg","https://devom-image.s3.ap-northeast-2.amazonaws.com/img/test/02.jpg","https://devom-image.s3.ap-northeast-2.amazonaws.com/img/test/01.jpg","https://devom-image.s3.ap-northeast-2.amazonaws.com/img/test/02.jpg"]
        post["count_comment"] = db.comment.count_documents({"post_id": post["_id"]})
        post["comment_list"] = list(db.comment.find({"post_id": post["_id"]}))
        for comment in post["comment_list"]:
            comment["_id"] = str(comment["_id"])
    #filename = str(datetime.today().strftime("%Y%m%d")) + "test"
    #print(filename)
    #filepath = "C:/Users/zxs37/Downloads/벤콘서트/278142579_675531963664734_3194712161371011802_n.jpg"
    # print(handle_upload_img(filepath,filename))

    # 포스팅 목록 받아오기
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})


@app.route('/update_like', methods=['POST'])
def update_like():
    # 좋아요 수 변경
    user_info = db.users.find_one({"username": "test"})
    post_id_receive = request.form["post_id_give"]
    type_receive = request.form["type_give"]
    action_receive = request.form["action_give"]
    doc = {
        "post_id": post_id_receive,
        "username": "test",
        "type": type_receive
    }
    print(doc)
    if action_receive == "like":
        db.likes.insert_one(doc)
    else:
        db.likes.delete_one(doc)
    count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
    return jsonify({"result": "success", 'msg': 'updated', "count": count})


def handle_upload_img(filepath,filenames):  # f = 파일명
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY
        )
        response = s3_client.upload_file(
            filepath, BUCKET_NAME, 'img/'+filenames+'.jpg',ExtraArgs={'ContentType': "image/jpg"},)
    except Exception as e:
        return e
    return True



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
