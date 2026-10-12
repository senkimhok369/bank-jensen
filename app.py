from flask import Flask, request, redirect, session
import sqlite3, random, os
from datetime import datetime
app = Flask(__name__)
app.secret_key = "bank_jensen_dewa_2026"
DB_PATH = "/tmp/bank.db"
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    os.makedirs("/tmp", exist_ok=True)
    conn=get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, balance INTEGER DEFAULT 100000000, account_no TEXT, is_blocked INTEGER DEFAULT 0, created_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS transaksi (id INTEGER PRIMARY KEY, from_user TEXT, to_user TEXT, amount INTEGER, note TEXT, created_at TEXT)")
    if not conn.execute("SELECT * FROM users WHERE username='admin'").fetchone():
        acc=str(random.randint(100,999))+"-"+str(random.randint(1000,9999))+"-"+str(random.randint(1000,9999))
        conn.execute("INSERT INTO users (username,password,balance,account_no,created_at) VALUES (?,?,?,?,?)",("admin","admin123",999999999999,acc,datetime.now().strftime("%d %b %Y")))
    conn.commit()
    conn.close()
init_db()
STYLE = "<style>body{background:#0a0e1a;color:white;font-family:sans-serif;padding:20px;margin:0} .card{background:#151a2d;padding:25px;border-radius:20px;max-width:400px;margin:20px auto;border:1px solid #c8a44a} input,button{width:100%;padding:14px;margin:8px 0;border-radius:12px;border:none;box-sizing:border-box} button{background:#c8a44a;color:#000;font-weight:bold;font-size:16px} a{color:#c8a44a;text-decoration:none} h1 span{color:#c8a44a}</style>"
@app.route("/")
def index():
    return STYLE + "<h1>BANK <span>JENSEN</span></h1><p>Private Bank Sultan Digital</p><div class=card><a href='/register'><button>Buka Rekening</button></a><a href='/login'><button style='background:transparent;border:1px solid #c8a44a;color:#c8a44a'>Login</button></a></div>"
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip()
        p=request.form["password"].strip()
        conn=get_db()
        user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone()
        conn.close()
        if user:
            session["user"]=dict(user)
            return redirect("/admin") if u=="admin" else redirect("/dashboard")
        return STYLE+"<div class=card>Salah! <a href=/login>Balik</a></div>"
    return STYLE+"<div class=card><h2>Login Bank Jensen</h2><form method=POST><input name=username placeholder='Username' required><input name=password type=password placeholder='Password' required><button>LOGIN</button></form><p>admin / admin123</p></div>"
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"].strip()
        p=request.form["password"].strip()
        acc=str(random.randint(100,999))+"-"+str(random.randint(1000,9999))+"-"+str(random.randint(1000,9999))
        try:
            conn=get_db()
            conn.execute("INSERT INTO users (username,password,account_no,created_at) VALUES (?,?,?,?)",(u,p,acc,datetime.now().strftime("%d %b %Y")))
            conn.commit()
            conn.close()
            return STYLE+"<div class=card>Berhasil "+u+"! No:"+acc+" <a href=/login><button>Login</button></a></div>"
        except:
            return STYLE+"<div class=card>Username ada! <a href=/register>Balik</a></div>"
    return STYLE+"<div class=card><h2>Buka Rekening</h2><form method=POST><input name=username placeholder='Username' required><input name=password type=password placeholder='Password' required><button>BUKA</button></form></div>"
@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/login")
    conn=get_db()
    user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    conn.close()
    return STYLE+f"<div class=card><h2>Halo {user['username']}</h2><p>{user['account_no']}</p><h1>Rp {user['balance']:,}</h1><a href=/transfer><button>Transfer</button></a><a href=/topup><button>TopUp</button></a><br><a href=/logout>Logout</a></div>"
@app.route("/transfer", methods=["GET","POST"])
def transfer():
    if "user" not in session: return redirect("/login")
    conn=get_db()
    me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    if request.method=="POST":
        to=request.form["to"].strip().lower()
        amt=int(request.form["amount"] or 0)
        target=conn.execute("SELECT * FROM users WHERE LOWER(username)=?",(to,)).fetchone()
        if target and me["balance"]>=amt:
            conn.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,me["id"]))
            conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(amt,target["id"]))
            conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",(me["username"],target["username"],amt,"transfer",datetime.now().strftime("%d %b %H:%M")))
            conn.commit()
            conn.close()
            return redirect("/dashboard")
        conn.close()
        return STYLE+"<div class=card>Gagal! <a href=/transfer>Balik</a></div>"
    conn.close()
    return STYLE+"<div class=card><h2>Transfer</h2><form method=POST><input name=to placeholder='Ke Username' required><input name=amount type=number required><button>Kirim</button></form></div>"
@app.route("/topup", methods=["GET","POST"])
def topup():
    if "user" not in session: return redirect("/login")
    if request.method=="POST":
        amt=int(request.form["amount"] or 0)
        conn=get_db()
        me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
        bonus=int(amt*0.1) if amt>=50000000 else 0
        total=amt+bonus
        conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(total,me["id"]))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return STYLE+"<div class=card><h2>TopUp Bonus 10%</h2><form method=POST><input name=amount type=number required><button>TopUp</button></form></div>"
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/admin")
def admin():
    if "user" not in session or session["user"]["username"]!="admin": return redirect("/login")
    conn=get_db()
    users=conn.execute("SELECT * FROM users WHERE username!='admin'").fetchall()
    conn.close()
    h=STYLE+"<div class=card><h2>ADMIN</h2>"
    for u in users: h+="<p>"+u["username"]+" Rp "+str(u["balance"])+"</p>"
    return h+"</div>"
