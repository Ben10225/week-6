from flask import Flask, render_template, redirect, request, session

import mysql.connector
from mysql_pwd import sqlPwd

app = Flask(__name__, static_folder="public", static_url_path="/")
app.debug = True

app.secret_key="anytxt"

# mydb = mysql.connector.connect(
#   host="localhost",    
#   user="root",  
#   passwd=sqlPwd(),  
#   database="week6"
# )

from mysql.connector import Error
from mysql.connector import pooling

def connectPool():
  connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host='localhost',
                                                user='root',
                                                database='week6',
                                                password=sqlPwd())
  connection_object = connection_pool.get_connection()   
  return connection_object                                          

# mycursor = connection_pool.cursor()
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

  db = connectPool()
  mycursor = db.cursor()
  mycursor.execute(showMsgSql)
  msgs = mycursor.fetchall()
  mycursor.close()
  db.close()

  # msgs = connectDB(None, None, False, True, False, False)
  time = []
  for i in msgs:
    s = str(i[2]).split(" ")[1][:5]
    time.append(s)
  return render_template("member.html", user=name, msgs=msgs, time=time, len=len(time) )


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

  db = connectPool()
  mycursor = db.cursor()
  mycursor.execute(signUpSelectSql, (name, ))
  exists = mycursor.fetchone()

  # exists = connectDB(signUpSelectSql, (name, ), True, False, False, False)
  if exists:
    mycursor.close()
    db.close()
    return {"result": "帳號已存在"}
  else:
    val = (name, username, password)
    mycursor.execute(insertSql, val)
    db.commit()
    mycursor.close()
    db.close()
    # connectDB(insertSql, val, False, False, True, False)
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

  # exists = connectDB(signInSelectSql, params, True, False, False, False)

  db = connectPool()
  mycursor = db.cursor(dictionary=True) 
  # db.cursor(dictionary=True) 資料 return 會變字典

  mycursor.execute(signInSelectSql, params)
  exists = mycursor.fetchone()
  mycursor.close()
  db.close()

  if not exists:
    return {"result": "帳號或密碼輸入錯誤"}
  
  session["name"] = exists["name"]
  return {"result": "OK"}
  


# 登出
@app.route("/signout")
def signout():
  session["name"] = False
  return redirect("/")


# 留言
@app.route("/message", methods=["post"])
def message():
  msg = request.json["msg"]
  clicked = request.json["click"]
  if not clicked:
    db = connectPool()
    mycursor = db.cursor()
    mycursor.execute(showMsgSql)
    msgs = mycursor.fetchall()
    mycursor.close()
    db.close()
    # msgs = connectDB(None, None, False, True, False, False)
    return {"result": msgs}
  if not msg:
    return {"result": "請留言"}
  
  name = session["name"]
  
  db = connectPool()
  mycursor = db.cursor()
  # 紀錄使用者及留言
  mycursor.execute(msgUidSelectSql, (name, ))
  uid = mycursor.fetchone()[0]
  val = (uid, msg)
  # 寫入
  mycursor.execute(msgSql, val)
  db.commit()
  # 抓所有留言
  mycursor.execute(showMsgSql)
  msgs = mycursor.fetchall()
  mycursor.close()
  db.close()
  # msgs = connectDB(msgUidSelectSql, (name, msg), False, False, False, True)

  # for i in msgs:
  #   print(i[0], i[1], i[2])
  return {"result": msgs}


app.run(port=3000)












# def connectDB(item1, item2, fetchonebool, memberbool, signupbool, msgbool):
#   try:
#     connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
#                                                   pool_size=5,
#                                                   pool_reset_session=True,
#                                                   host='localhost',
#                                                   user='root',
#                                                   database='week6',
#                                                   password=sqlPwd())

#     # print("Printing connection pool properties ")
#     # print("Connection Pool Name - ", connection_pool.pool_name)
#     # print("Connection Pool Size - ", connection_pool.pool_size)

#     # Get connection object from a pool
#     connection_object = connection_pool.get_connection()

#     if connection_object.is_connected():

#       mycursor = connection_object.cursor()
#       if fetchonebool:
#         mycursor.execute(item1, item2)
#         exists = mycursor.fetchone()
#         return exists

#       if memberbool:
#         mycursor.execute(showMsgSql)
#         msgs = mycursor.fetchall()
#         return msgs
        
#       if signupbool:
#         mycursor.execute(item1, item2)
#         connection_object.commit()

#       if msgbool:
#         mycursor.execute(item1, (item2[0], ))
#         uid = mycursor.fetchone()[0]
#         mycursor.execute(msgSql, (uid, item2[1]))
#         connection_object.commit()

#         mycursor.execute(showMsgSql)
#         msgs = mycursor.fetchall()
#         return msgs

#   except Error as e:
#     print("Error while connecting to MySQL using Connection pool ", e)
#   finally:
#     if connection_object.is_connected():
#       mycursor.close()
#       connection_object.close()
#       print("MySQL connection is closed")