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
        acc=f"{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        conn.execute("INSERT INTO users (username,password,balance,account_no,created_at) VALUES (?,?,?,?,?)",("admin","admin123",999999999999,acc,datetime.now().strftime("%d %b %Y")))
    conn.commit()
    conn.close()
init_db()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap');
*{font-family:'Outfit',sans-serif;box-sizing:border-box}
body{background:#070a14;color:#e8e8e8;margin:0;min-height:100vh}
.nav{background:#0f1325;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #c8a44a33;position:sticky;top:0;z-index:99}
.nav b{color:#c8a44a;font-size:20px;letter-spacing:2px}
.container{max-width:480px;margin:0 auto;padding:20px}
.card{background:linear-gradient(145deg,#151a2d,#1a2040);padding:24px;border-radius:22px;border:1px solid #c8a44a33;margin:16px 0;box-shadow:0 10px 30px #0008}
.card-gold{background:linear-gradient(145deg,#c8a44a,#a6832d);color:#000}
.btn{width:100%;padding:14px;border:none;border-radius:14px;font-weight:700;font-size:15px;cursor:pointer;margin:8px 0;display:block;text-align:center;text-decoration:none}
.btn-gold{background:#c8a44a;color:#000}
.btn-outline{background:transparent;border:1px solid #c8a44a;color:#c8a44a}
.btn-dark{background:#0a0e1a;color:#fff;border:1px solid #333}
input,select{width:100%;padding:14px;border-radius:14px;border:1px solid #2a2f4a;background:#0a0e1a;color:#fff;margin:8px 0;font-size:15px}
h1,h2{margin:10px 0}
.badge{display:inline-block;background:#c8a44a22;color:#c8a44a;padding:4px 10px;border-radius:20px;font-size:12px;border:1px solid #c8a44a44}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stat{text-align:center}
.stat h2{color:#c8a44a;font-size:28px}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:10px;border-bottom:1px solid #222;text-align:left}
a{color:#c8a44a;text-decoration:none}
</style>
"""

def page(content, user=None):
    nav = f"<div class=nav><b>BANK JENSEN</b><span>{user['username'] if user else 'GUEST'} <a href='/logout' style='margin-left:12px;color:#ff6b6b'>Logout</a></span></div>" if user or True else ""
    return f"<!DOCTYPE html><html><head><meta name=viewport content='width=device-width,initial-scale=1'>{CSS}</head><body>{nav}<div class=container>{content}</div></body></html>"

@app.route("/")
def index():
    return page(f"<h1 style='font-size:36px'>BANK<br><span style='color:#c8a44a'>JENSEN</span></h1><p style='opacity:.7'>Private Bank Sultan Digital • Aman • Cepat • Elit</p><div class=card><div class=grid2><div class=stat><h2>100+</h2><small>Nasabah Sultan</small></div><div class=stat><h2>24/7</h2><small>Online</small></div></div></div><div class=card><a href='/register' class='btn btn-gold'>BUKA REKENING GRATIS</a><a href='/login' class='btn btn-outline'>LOGIN</a><p style='text-align:center;margin-top:12px;font-size:12px;opacity:.6'>admin / admin123 untuk demo admin</p></div>")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip();p=request.form["password"].strip()
        conn=get_db();user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone();conn.close()
        if user:
            if user["is_blocked"]: return page("<div class=card>Rekening diblokir admin! Hubungi pusat.</div>")
            session["user"]=dict(user)
            return redirect("/admin") if u=="admin" else redirect("/dashboard")
        return page("<div class=card style='border-color:#ff4444'>Username / Password salah!<br><br><a href='/login' class='btn btn-outline'>Coba Lagi</a></div>")
    return page("<div class=card><h2>Login Bank Jensen</h2><span class=badge>Secure Banking</span><form method=POST style='margin-top:16px'><input name=username placeholder='Username' required><input name=password type=password placeholder='Password' required><button class='btn btn-gold'>LOGIN SULTAN</button></form><br><a href='/register'>Belum punya rekening? Buka disini</a><br><br><small style='opacity:.5'>Demo Admin: admin / admin123</small></div>")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"].strip();p=request.form["password"].strip()
        if len(u)<3: return page("<div class=card>Username minimal 3 huruf <a href='/register'>Balik</a></div>")
        acc=f"{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        try:
            conn=get_db();conn.execute("INSERT INTO users (username,password,account_no,created_at) VALUES (?,?,?,?)",(u,p,acc,datetime.now().strftime("%d %b %Y")));conn.commit();conn.close()
            return page(f"<div class=card card-gold><h2>🎉 REKENING JADI!</h2><p>Username: <b>{u}</b><br>No Rek: <b>{acc}</b><br>Saldo Awal: <b>Rp 100.000.000</b></p><a href='/login' class='btn btn-dark'>Login Sekarang</a></div>")
        except:
            return page("<div class=card>Username sudah dipakai! <a href='/register'>Ganti lain</a></div>")
    return page("<div class=card><h2>Buka Rekening Sultan</h2><p style='opacity:.7'>Dapat Rp 100jt saldo awal + Bonus</p><form method=POST><input name=username placeholder='Pilih Username' required><input name=password type=password placeholder='Buat Password' required><button class='btn btn-gold'>BUKA REKENING</button></form><br><a href='/login'>Sudah punya? Login</a></div>")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC LIMIT 8",(user["username"],user["username"])).fetchall();conn.close()
    session["user"]=dict(user)
    tx_html = "".join([f"<tr><td>{t['created_at']}</td><td>{'⬇️' if t['to_user']==user['username'] else '⬆️'} {t['from_user'] if t['to_user']==user['username'] else t['to_user']}<br><small style='opacity:.5'>{t['note']}</small></td><td style='color:{'#4ade80' if t['to_user']==user['username'] else '#ff6b6b'}'>Rp {t['amount']:,}</td></tr>" for t in tx]) or "<tr><td colspan=3 style='text-align:center;opacity:.5'>Belum ada transaksi</td></tr>"
    return page(f"<div class=card card-gold><small>{user['account_no']} • {user['created_at']}</small><h2 style='margin:6px 0'>Halo, {user['username']} 👑</h2><h1 style='font-size:32px'>Rp {user['balance']:,}</h1><span class=badge style='background:#0003;color:#000;border-color:#0003'>Saldo Aktif</span></div><div class=card><div class=grid2><a href='/transfer' class='btn btn-gold'>💸 Transfer</a><a href='/topup' class='btn btn-dark'>💰 TopUp</a><a href='/qris' class='btn btn-dark'>📱 QRIS</a><a href='/history' class='btn btn-dark'>📜 History</a></div></div><div class=card><h3>Transaksi Terakhir</h3><table><tr><th>Tgl</th><th>Detail</th><th>Nominal</th></tr>{tx_html}</table><br><a href='/history' class='btn btn-outline'>Lihat Semua</a></div>", user=user)

@app.route("/transfer", methods=["GET","POST"])
def transfer():
    if "user" not in session: return redirect("/login")
    conn=get_db();me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    all_u=conn.execute("SELECT username FROM users WHERE id!=?",(me["id"],)).fetchall()
    msg=""
    if request.method=="POST":
        to=request.form["to"].strip().lower();amt=int(request.form["amount"] or 0);note=request.form["note"].strip() or "Transfer"
        target=conn.execute("SELECT * FROM users WHERE LOWER(username)=?",(to,)).fetchone()
        if not target: msg=f"<div class=card style='border-color:#ff4444'>User {to} tidak ketemu! Yang ada: {', '.join([u['username'] for u in all_u])}</div>"
        elif me["balance"]<amt: msg="<div class=card style='border-color:#ff4444'>Saldo tidak cukup!</div>"
        elif target["id"]==me["id"]: msg="<div class=card style='border-color:#ff4444'>Gak bisa transfer ke diri sendiri!</div>"
        else:
            conn.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,me["id"]));conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(amt,target["id"]))
            conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",(me["username"],target["username"],amt,note,datetime.now().strftime("%d %b %H:%M")))
            conn.commit();conn.close()
            return redirect("/dashboard")
    conn.close()
    options = "".join([f"<option value='{u['username']}'>{u['username']}</option>" for u in all_u])
    return page(f"{msg}<div class=card><h2>💸 Transfer Sultan</h2><form method=POST><label>Ke Username</label><input list=userlist name=to placeholder='Ketik username' required><datalist id=userlist>{options}</datalist><label>Nominal</label><input name=amount type=number placeholder='100000' required><label>Catatan</label><input name=note placeholder='Buat makan sultan'><button class='btn btn-gold'>KIRIM SEKARANG</button></form><br><small style='opacity:.5'>User tersedia: {', '.join([u['username'] for u in all_u]) or 'Belum ada'}</small></div><a href='/dashboard' class='btn btn-outline'>← Dashboard</a>", user=me)

@app.route("/topup", methods=["GET","POST"])
def topup():
    if "user" not in session: return redirect("/login")
    conn=get_db();me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    if request.method=="POST":
        amt=int(request.form["amount"] or 0);method=request.form["method"]
        if amt<10000:
            conn.close()
            return page("<div class=card>Minimal 10rb! <a href='/topup'>Balik</a></div>", user=me)
        bonus=int(amt*0.1) if amt>=50000000 else 0;total=amt+bonus
        conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(total,me["id"]))
        conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",("BANK JENSEN",me["username"],total,f"TopUp {method} Bonus {bonus}",datetime.now().strftime("%d %b %H:%M")))
        conn.commit();conn.close()
        return redirect("/dashboard")
    conn.close()
    return page("<div class=card><h2>💰 TopUp Sultan</h2><p><span class=badge>Bonus 10% jika >=50jt</span></p><form method=POST><label>Nominal</label><input name=amount type=number placeholder='50000000' required><label>Metode</label><select name=method><option>BCA VA</option><option>GoPay</option><option>OVO</option><option>QRIS</option></select><button class='btn btn-gold'>TOPUP SEKARANG</button></form></div><a href='/dashboard' class='btn btn-outline'>← Dashboard</a>", user=me)

@app.route("/qris")
def qris():
    if "user" not in session: return redirect("/login")
    u=session["user"]
    return page(f"<div class=card style='text-align:center'><h2>📱 QRIS BANK JENSEN</h2><p>{u['account_no']}<br>{u['username']}</p><div style='background:white;padding:20px;border-radius:16px;margin:20px auto;max-width:280px'><img src='https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=BANKJENSEN-{u['username']}-{u['account_no']}' style='width:100%'></div><p style='opacity:.6'>Scan untuk transfer ke {u['username']}</p></div><a href='/dashboard' class='btn btn-outline'>← Dashboard</a>", user=u)

@app.route("/history")
def history():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC",(user["username"],user["username"])).fetchall();conn.close()
    rows="".join([f"<tr><td>{t['created_at']}</td><td>{t['from_user']} → {t['to_user']}<br><small>{t['note']}</small></td><td>Rp {t['amount']:,}</td></tr>" for t in tx])
    return page(f"<div class=card><h2>📜 History {user['username']}</h2><p>Saldo: Rp {user['balance']:,}</p><table><tr><th>Waktu</th><th>Transaksi</th><th>Nominal</th></tr>{rows or '<tr><td colspan=3> Kosong </td></tr>'}</table></div><a href='/dashboard' class='btn btn-outline'>← Dashboard</a> <a href='/export-pdf' class='btn btn-gold'>Export PDF</a>", user=user)

@app.route("/export-pdf")
def export_pdf():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC",(user["username"],user["username"])).fetchall();conn.close()
    html=f"<html><body style='font-family:monospace;padding:20px'><h1>BANK JENSEN - {user['username'].upper()}</h1><p>{user['account_no']} | Saldo Rp {user['balance']:,} | {datetime.now()}</p><table border=1 cellpadding=8 style='width:100%;border-collapse:collapse'><tr><th>Tgl</th><th>Dari</th><th>Ke</th><th>Note</th><th>Nominal</th></tr>"
    for t in tx: html+=f"<tr><td>{t['created_at']}</td><td>{t['from_user']}</td><td>{t['to_user']}</td><td>{t['note']}</td><td>Rp {t['amount']:,}</td></tr>"
    html+="</table></body></html>"
    return html

@app.route("/admin")
def admin():
    if "user" not in session or session["user"]["username"]!="admin": return redirect("/login")
    conn=get_db();users=conn.execute("SELECT * FROM users WHERE username!='admin' ORDER BY id DESC").fetchall();total=conn.execute("SELECT COUNT(*), SUM(balance) FROM users WHERE username!='admin'").fetchone();conn.close()
    cards="".join([f"<div class=card><b>{u['username']}</b> <small>{u['account_no']}</small><br>Rp {u['balance']:,} {'🔒 BLOCKED' if u['is_blocked'] else '✅ Aktif'}<br><br><div class=grid2><a href='/admin/add/{u['id']}' class='btn btn-gold' style='padding:8px;font-size:12px'>+10jt</a><a href='/admin/block/{u['id']}' class='btn btn-dark' style='padding:8px;font-size:12px'>{'Unblock' if u['is_blocked'] else 'Block'}</a></div></div>" for u in users])
    return page(f"<div class=card card-gold><h2>👑 ADMIN DEWA</h2><p>Total Nasabah: {total[0] or 0} | Total Saldo: Rp {total[1] or 0:,}</p><a href='/admin/bunga' class='btn btn-dark'>💸 Bagi Bunga 5% Semua</a></div>{cards or '<div class=card>Belum ada nasabah</div>'}", user=session["user"])

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
    if session.get("user",{}).get("username")!="admin": return redirect("/login")
    conn=get_db();conn.execute("UPDATE users SET balance=balance+10000000 WHERE id=?",(id,));conn.commit();conn.close();return redirect("/admin")

@app.route("/logout")
def logout(): session.clear();return redirect("/login")
