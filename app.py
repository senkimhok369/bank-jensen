from flask import Flask, render_template, request, redirect, session, flash, send_file
import sqlite3, random, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bank_jensen_dewa_2026"

# FIX UNTUK VERCEL - PAKAI /tmp
DB_PATH = "/tmp/bank.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # bikin folder /tmp kalo belum ada
    os.makedirs("/tmp", exist_ok=True)
    conn=get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, balance INTEGER DEFAULT 100000000, account_no TEXT, is_blocked INTEGER DEFAULT 0, created_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS transaksi (id INTEGER PRIMARY KEY, from_user TEXT, to_user TEXT, amount INTEGER, note TEXT, created_at TEXT)")
    if not conn.execute("SELECT * FROM users WHERE username='admin'").fetchone():
        acc=f"{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        conn.execute("INSERT INTO users (username,password,balance,account_no,created_at) VALUES (?,?,?,?,?)",("admin","admin123",999999999999,acc,datetime.now().strftime("%d %b %Y")))
    conn.commit();conn.close()

init_db()

@app.route("/")
def index(): return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip();p=request.form["password"].strip()
        conn=get_db();user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone();conn.close()
        if user:
            if user["is_blocked"]: flash("Rekening diblokir!");return redirect("/login")
            session["user"]=dict(user)
            return redirect("/admin") if u=="admin" else redirect("/dashboard")
        flash("Username / Password salah")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"].strip();p=request.form["password"].strip()
        acc=f"{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        try:
            conn=get_db();conn.execute("INSERT INTO users (username,password,account_no,created_at) VALUES (?,?,?,?)",(u,p,acc,datetime.now().strftime("%d %b %Y")));conn.commit();conn.close()
            flash("Rekening berhasil dibuat!");return redirect("/login")
        except: flash("Username sudah terdaftar!")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC LIMIT 5",(user["username"],user["username"])).fetchall();conn.close()
    session["user"]=dict(user);return render_template("dashboard.html",user=user,tx=tx)

@app.route("/transfer", methods=["GET","POST"])
def transfer():
    if "user" not in session: return redirect("/login")
    conn=get_db();me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    all_users=conn.execute("SELECT username FROM users WHERE id!=?",(me["id"],)).fetchall()
    if request.method=="POST":
        to=request.form["to"].strip().lower();amt=int(request.form["amount"] or 0);note=request.form["note"].strip()
        target=conn.execute("SELECT * FROM users WHERE LOWER(username)=?",(to,)).fetchone()
        if not target: flash(f"Tidak ketemu! Ada: {', '.join([u['username'] for u in all_users])}")
        elif me["balance"]<amt: flash("Saldo tidak cukup!")
        elif target["id"]==me["id"]: flash("Gak bisa ke diri sendiri!")
        else:
            conn.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,me["id"]));conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(amt,target["id"]))
            conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",(me["username"],target["username"],amt,note,datetime.now().strftime("%d %b %H:%M")))
            conn.commit();conn.close();return redirect("/dashboard")
    conn.close();return render_template("transfer.html",user=me,all_users=all_users)

@app.route("/topup", methods=["GET","POST"])
def topup():
    if "user" not in session: return redirect("/login")
    conn=get_db();me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    if request.method=="POST":
        amt=int(request.form["amount"] or 0);method=request.form["method"]
        if amt<10000: flash("Minimal 10rb!")
        else:
            bonus=int(amt*0.1) if amt>=50000000 else 0;total=amt+bonus
            conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(total,me["id"]))
            conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",("BANK JENSEN",me["username"],total,f"TopUp {method} Bonus {bonus}",datetime.now().strftime("%d %b %H:%M")))
            conn.commit();conn.close();return redirect("/dashboard")
    conn.close();return render_template("topup.html",user=me)

@app.route("/qris")
def qris():
    if "user" not in session: return redirect("/login")
    return render_template("qris.html",user=session["user"])

@app.route("/scan")
def scan():
 if "user" not in session: return redirect("/login")
 return render_template("scan.html", user=session["user"])

@app.route("/history")
def history():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC",(user["username"],user["username"])).fetchall();conn.close()
    return render_template("history.html",user=user,tx=tx)

@app.route("/export-pdf")
def export_pdf():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC",(user["username"],user["username"])).fetchall();conn.close()
    html=f"<html><body style='font-family:monospace;padding:20px'><h1>BANK JENSEN - KORAN {user['username'].upper()}</h1><p>{user['account_no']} | Saldo Rp {user['balance']:,} | {datetime.now()}</p><table border=1 cellpadding=8 style='width:100%;border-collapse:collapse'><tr><th>Tgl</th><th>Dari</th><th>Ke</th><th>Note</th><th>Nominal</th></tr>"
    for t in tx: html+=f"<tr><td>{t['created_at']}</td><td>{t['from_user']}</td><td>{t['to_user']}</td><td>{t['note']}</td><td>Rp {t['amount']:,}</td></tr>"
    html+="</table></body></html>"
    return html

@app.route("/admin")
def admin():
    if "user" not in session or session["user"]["username"]!="admin": return redirect("/login")
    conn=get_db();users=conn.execute("SELECT * FROM users WHERE username!='admin' ORDER BY id DESC").fetchall();total=conn.execute("SELECT COUNT(*), SUM(balance) FROM users WHERE username!='admin'").fetchone();conn.close()
    return render_template("admin.html",users=users,total=total)

@app.route("/admin/bunga")
def bunga():
    if session.get("user",{}).get("username")!="admin": return redirect("/login")
    conn=get_db()
    for u in conn.execute("SELECT * FROM users WHERE username!='admin'").fetchall():
        bonus=int(u["balance"]*0.05);conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(bonus,u["id"]));conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",("BANK JENSEN",u["username"],bonus,"Bunga Sultan 5%",datetime.now().strftime("%d %b %H:%M")))
    conn.commit();conn.close();return redirect("/admin")

@app.route("/admin/block/<int:id>")
def block_user(id):
    if session.get("user",{}).get("username")!="admin": return redirect("/login")
    conn=get_db();cur=conn.execute("SELECT is_blocked FROM users WHERE id=?",(id,)).fetchone();conn.execute("UPDATE users SET is_blocked=? WHERE id=?",(0 if cur["is_blocked"] else 1,id));conn.commit();conn.close();return redirect("/admin")

@app.route("/admin/add/<int:id>")
def add_money(id):
    conn=get_db();conn.execute("UPDATE users SET balance=balance+10000000 WHERE id=?",(id,));conn.commit();conn.close();return redirect("/admin")

@app.route("/logout")
def logout(): session.clear();return redirect("/login")
