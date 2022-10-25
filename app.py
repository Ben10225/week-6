from email import message
from flask import Flask, render_template, redirect, request, session

import mysql.connector
from mysql_pwd import sqlPwd

app = Flask(__name__, static_folder="public", static_url_path="/")
app.debug = True

app.secret_key="anytxt"

mydb = mysql.connector.connect(
  host="localhost",    
  user="root",  
  passwd=sqlPwd(),  
  database="week6"
)

mycursor = mydb.cursor()
insertSql = "INSERT INTO users (name, username, password) VALUES (%s, %s, %s)"
signUpSelectSql = "SELECT * FROM users WHERE username=%s"
msgSql = "INSERT INTO message (name_id, msg) VALUES (%s, %s)"
showMsgSql = "SELECT u.name, m.msg, m.time FROM users AS u INNER JOIN message As m ON u.uid=m.name_id ORDER BY m.time DESC"
showMsgParamsSql = ()
signInSelectSql = "SELECT * FROM users WHERE username=%s and password=%s"
msgUidSelectSql = "SELECT uid FROM users WHERE name=%s"

# 首頁
@app.route("/")
def index():
  return render_template("index.html")


# 會員頁
@app.route("/member")
def member():
  name = session["name"]
  if not name:
    return redirect("/")
  
  mycursor.execute(showMsgSql)
  msgs = mycursor.fetchall()
  return render_template("member.html", user=name, msgs=msgs)


# 錯誤頁
@app.route("/error")
def error():
  err = request.args.get("message", "輸入錯誤")
  return render_template("error.html", message=err)


# 註冊
@app.route("/signup", methods=["post"])
def signup():
  name = request.json["name"]
  username = request.json['username']
  password = request.json['password']
  if name == "" or username == "" or password == "":
    return {"result": "請輸入註冊資訊"}
  mycursor.execute(signUpSelectSql, (name, ))
  exists = mycursor.fetchone()
  if exists:
    return {"result": "帳號已存在"}
  else:
    val = (name, username, password)
    mycursor.execute(insertSql, val)
    mydb.commit()
    print("用戶 {} 帳戶創建成功！".format(name))
    return {"result": "OK"}


# 登入
@app.route("/signin", methods=["post"])
def sign():
  username = request.json['username']
  password = request.json['password']
  if username == "" or password == "":
    return {"result": "請輸入登入資訊"}
  params = (username, password)
  mycursor.execute(signInSelectSql, params)
  exists = mycursor.fetchone()
  if not exists:
    return {"result": "帳號或密碼輸入錯誤"}
  
  session["name"] = exists[1]
  return {"result": "OK"}


# 登出
@app.route("/signout")
def signout():
  session["name"] = False
  return redirect("/")


# 留言
@app.route("/message", methods=["post"])
def stayMsg():
  name = session["name"]
  mycursor.execute(msgUidSelectSql, (name, ))
  uid = mycursor.fetchone()[0]

  msg = request.json["msg"]
  clicked = request.json["click"]
  if not clicked:
    mycursor.execute(showMsgSql)
    msgs = mycursor.fetchall()
    return {"result": msgs}
  if not msg:
    return {"result": "請留言"}
  valMsg = (uid, msg)
  mycursor.execute(msgSql, valMsg)
  mydb.commit()

  mycursor.execute(showMsgSql)
  msgs = mycursor.fetchall()
  # for i in msgs:
  #   print(i[0], i[1], i[2])
  return {"result": msgs}


app.run(port=3000)

