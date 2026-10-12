from flask import Flask, request, redirect, session
import sqlite3, random, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bank_jensen_pin_dewa"
DB_PATH = "/tmp/bank.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("/tmp", exist_ok=True)
    conn=get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, pin TEXT DEFAULT '123456', balance INTEGER DEFAULT 100000000, account_no TEXT, is_blocked INTEGER DEFAULT 0, created_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS transaksi (id INTEGER PRIMARY KEY, from_user TEXT, to_user TEXT, amount INTEGER, note TEXT, created_at TEXT)")
    try:
        conn.execute("ALTER TABLE users ADD COLUMN pin TEXT DEFAULT '123456'")
    except: pass
    if not conn.execute("SELECT * FROM users WHERE username='admin'").fetchone():
        acc=f"{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        conn.execute("INSERT INTO users (username,password,pin,balance,account_no,created_at) VALUES (?,?,?,?,?,?)",("admin","admin123","123456",999999999999,acc,datetime.now().strftime("%d %b %Y")))
    conn.commit()
    conn.close()
init_db()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap');
*{font-family:'Outfit',sans-serif;box-sizing:border-box}
body{background:#070a14;color:#e8e8e8;margin:0;min-height:100vh}
.nav{background:#0f1325;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #c8a44a33;position:sticky;top:0;z-index:99}
.nav b{color:#c8a44a;font-size:20px;letter-spacing:2px}
.container{max-width:480px;margin:0 auto;padding:20px}
.card{background:linear-gradient(145deg,#151a2d,#1a2040);padding:24px;border-radius:22px;border:2px solid #c8a44a33;margin:16px 0;box-shadow:0 10px 30px #0008}
.card-gold{background:linear-gradient(145deg,#c8a44a,#a6832d);color:#000}
.btn{width:100%;padding:14px;border:none;border-radius:14px;font-weight:700;font-size:15px;cursor:pointer;margin:8px 0;display:block;text-align:center;text-decoration:none}
.btn-gold{background:#c8a44a;color:#000}
.btn-outline{background:transparent;border:2px solid #c8a44a;color:#c8a44a}
.btn-dark{background:#0a0e1a;color:#fff;border:1px solid #333}
input,select{width:100%;padding:14px;border-radius:14px;border:1px solid #2a2f4a;background:#0a0e1a;color:#fff;margin:8px 0;font-size:15px}
h1,h2{margin:10px 0}
.badge{display:inline-block;background:#c8a44a22;color:#c8a44a;padding:4px 10px;border-radius:20px;font-size:12px;border:2px solid #c8a44a44}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stat{text-align:center}
.stat h2{color:#c8a44a;font-size:28px}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:10px;border-bottom:1px solid #222;text-align:left}
a{color:#c8a44a;text-decoration:none}
.pin-dots{display:flex;gap:8px;justify-content:center;margin:12px 0}
.pin-dots div{width:14px;height:14px;border-radius:50%;background:#222;border:2px solid #c8a44a44}
</style>
"""

def page(content, user=None):
    logo = "<span style='display:flex;align-items:center;gap:10px'><img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAsEElEQVR4nO2dd3hcxdWH37ll+2qlVZcsWbJkW5I7rhiDTWx6DWAIgUBICCUFQhp8QEJIwkdNgQChh+RLIPSOMcGmGdx7t9Ulq9ft5Zbvj13JMhhwgMg2z77Ps4+k1d17Z+/87sycM2fOQIoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKQ4/xMEuwDAgki9pyHtm8rW/44YeY+znuK8UX0UBDFS2IFGBxuA/xJAvvL9vbiaVsW+VC0DmKyqIr5IApORLg6QKJMH4ouL0bS19pfG4Ngb0UUARyNlgehPHSyQ10gdGF0jNIGoURdpdkuWsreto7zRMc6go5OTPr4QYDncBDDztBmAK4FcLqyy3v9A4I6LpC4CjHS77uMIcV25JUTpFeS7yMu1kZ9hxuyzI6AghoekG/qCGL6zT1h2iocVHQ5OP5jZfb39/ZAeYy2RZfuu4qTkrFq+u9n1EDIe1EA5nAciADoknPcPlndbti5+vqNKpo0Z6xsycmMPMiTmMLsnA47Kim0Lv7Y+abR1+OruDBCO6iETjgIkiS7gcKrk5HjPba8ebZhEWiyQFQxFR2+hnzdZuVmxqZ2dt955IKL7Y6bT8KxCYv1SIZ/QhZTkshXA4CkBioKs2TcntzjkrEIhcmZvj/Nqp88s5cW4xRTl2s6cvqq/a2CJWbGyTttX0idbOEPGoPngGRZVQZRkTE1030XQDUzPANJFUmRyvnYpR6easSTnGzMkjzPxcp9TZE5aWLm/hlaXVVNf2bLRa1YfOOXbMP/75xipfsmyDojxcOJwEMNDc67IkcLmzFvb7I9dWlGdOvfCMCuZNz8MfMbRXltRIr79dJ9U3+UBAQZ6bsmIPxQVpZHsdpLusYCTqSFUUdF0DAZKkEIlrBEMxenwxmtv8VDf20djix4xr5OS6OP6oYvPrJ4zRi/Jd0rptndLfnt3Oqg0t9bIq/enOS2c9cPWf34hymLUGh4sABkdqRXl505raw7eOGulZcPl5lSyYU6xv3NXDg//cIK9c145iVZhcmc0RVdkU5rkwEPT0hWnvDNLeHcLnj+EPxojFdTTdxDRNLKqMIkvYbTIZaTayvQ5ys+xkee2okkRHV5ANu7pZt7WTUCBMxZhsLjm7yjjuqGJz4/Yu+e6/b2TTto5N2en2Gzt72l8xElV/WLQGh4MAZEBf8+Bl6tE/ee6XQpjXXXrOOPXyCyfrq9bvEbc/uFraUd1Fbl4aJx41kvGjs+kPRNi8q4td9X109ISJRDUEAlkWyLKELAuEECiyQJIE0ZiOAHQj0RXoSWGoqkRWup2yojQmVOSQl+mkuqGbf3/YRE1dN3l5afz0kqnGaSeMNl5aXK3c8dBq+vuj/7dgfPZP39hQ3QkoJK2SQ5VDXQAKoE0ZPbJyQ23vY5Orcmbd9YujkISp33j3CvmD1c0UjUjj7BPGUpBlZ8vuLlZt7mBPexATsFllVEVGlgRCJOx7wzSRhKC5zc/d/zOX8uJ0TvvBy+RlO8FMDCgRgAmGYRLXDSJRDcOAnEw7U6uymDw2m2BE57X3Gti0tZXKMTncfPVMY1Shm1/evUp684PGuuK8tMvqGhvf4hDvEg5VAQw4X7TCvMKz2noCj3zvnHEZ131ninb/M1vkOx5ZLxx2hW+dXsmYkWms2tzBO6ub8QXjOO0qVlVKeG0ME0kSxGI6kZiOYSSae5dDJT3Nwn03zKO4wMM3f76I5o4AgVCcWExHCIFFlbBZFUzTRJAQUFwzCIbjWFSJGRNymX9kCR09YZ54ZQctrb2cf3olv7v6SO25N2uVX9+72rQq0s/7fR2/N8y9A9eDelf3w6EoAAFIQqB707N/FtHMO/947VHMnpSrX3LjEnn1xhaOnjmSc44rY2tNLy8uqSYQ0khzWZAlgW7svceSEATDGgU5DsaXe3E6LOxq6KOlI8hrD5xOb0+YaFynuMjDRT9/g95AjGnjstF1k90NfVQ3+rBZ5cHWA5ItBOAPxpCE4LjZxcybUcTSlU08v2gnRSPSePyWBYammVx8wxLJ748/EA33XKkZxsC9PqREcKgJYMCBp7vTsm9RVXH9k7cfr2uGIb7x88VSIKxxxbnjKc538/eXt1PT5CPdbf1YxcuyQNdNAqE4X58/igtOq6C9K0CXL0phrpPe3ghLV+5Bi2vkZTvYWd/PWQvKyc5x0tYewCILSosyeHdVEw88vQlVVVAVCcMwPyaEPl+UzAwb3/76OCTg3ic20dMX4Z7rjzIXHDlSP+vqRUptQ98zH9xz7gXTLn9I5xBrCQ41AShCoKW5vLc63bbrXvnzKdr6HR3ypb9aKnKz7Fx94WTqW/w8+douVFXCblPQ9b33cuBJ7fNHSXNamDUpj59ePJnq+l56gnEMScbfF2bsyDQ27OxhXLmXolwXz/y7mmNnFLKjtheby4ZVAqsqUTUqg2ferObpxdWEwhpOh4oqSxjmvmKLxw18wRinzC1l3vQCHn5mG5u2tXPdlTP5/nkT46f/8BV1++6e5yKRnoVCiEHP5fDf3o+jHOwCDEERoKW7s69TrOK6V+89RftgY5v8o5uXiDFlmfzwgkm89m49b69uIivdgWkyWPlicNAGMU3nt1fPJjfTgc8XIhCOsn5nN++sbiEUiSNJAkWWmFyRxV3XzQG3lSUrm7j+T8uxqDLRuI7bYWHi2Gzys51Mr8qhqjwLu03h1/euIBTRsKgymCYmiTLIkiAr3c5r79ZR29jH98+fwL8W2bjtL8vx+aPqa/efET/pylfOdjmyH5MkcYlhmAoJE/Ggi0D67EOGBRnQsrNyzo+Zxq3P/vEkbfWWdvlHNy8VEypz+PFFU/jbi9t4b20LOV5nsilO3DvTTAzOFFUmFIlz7w3HMrYkg6t/+zaGYdDbH6XHF2VnQy/RuE53X4T6PT56fZGkd8EkEjdobPHT0RMmGtOpbuynoztAvz+Mw2nhN/evors3zD9uOz5hOoqEyWgkux0T0HSDrHQ7Nc0+bn1oNeeeOJYT5pVz/z/WcMdjq9UX7zk5np1t/7bHnfMbkTAN5U+6GcPJoSAACdDHFBZO7PFFH/3LTfOM/pAuX37zO6JyTBZXfmMi9z+5iZ31/WR6bGja4OwupgmqIpGZbqe51c/cqYVMrczmwl8sIhI32FrThyQYNAN9gTgnHz2Sre9+l4tOr2T1uhZa63ooK3RSvfxyrvrWZCJRHc0wkCQJm1VmV10vMU3nF3ctIxyJc+nZ49jT0ofbqeKwq/t0B5pu4Hao+EMav/3Lcs5YMJr5c8q5+/FV/Ou1rcpTdy7QdLRfZnmzz+EQEcHBFoAAxDULZ9l3tfqeuOqiyfYjqnLNC3++SBTmOrnqwik88uwWGlr8pLutaLqx74cFhKMat//kSO6/aS6V5Zm8ubwJX1+ErAw7Dz29BVlVue7yGcyZkke6W+WHF06mNNdJeUkG/lCcmrpepk4oIF2VuPbS6WRl2Jg1IYcrvjGBGZMK+d+H1+C0q2AYLPqgkYLcNH526XSevPNE5OSYQwwZSemGic0qE43p3PbgCs49aSxTJxVx/R9Xio7+qHT3/xxjdPsij8wYU1xKYixwUOvgYA8CZQG6xZbxhynjsq957u6TtZMvf0nZUdPDLdfM4d/Lm3h/TTNej+1jlQ8gCYjEDEbk2Nn42oXc8cBa7HaFOUeN5Pzvv4rLoXDDFTMozHEgC7j1kbWoqsxp80bx1+c28/z9p2N1qnz/+n8zIseFoso8+2Y1f73leEzTIBIzuPWh1Xy4vpV//eFEJAmeenUnD/3pFBZ+9wUWLWsi3W3ZxwIZ/GKSIBCOU5zn4opzJ/C7B1cTj+t88MR5+m2PrZf/9vzmt/VY//zkoPCguYwPpvpkQM/PLphtsco//vMNx+i3Pbxa3ri1lSsvmEx1k493VjV9YuUDGCY4bArb6/r57nVLmD11BJPGZCMrClXlmeRmOWjtChGJaPz2gVVs3d1NZWkGF1//Jk1tIdZsamP9pnZ21fdz872raO8JUZTv4hs/WwRCYtWmFkYWuBmR7yIrw4HTbuWCM6q4/Y/LeWFJHRlp1v1WPiRaArfDQk1TP6+8W8fVFx1Bb1+YK29+S/7V96ZopSM8x3o8WZeTqPyD1hUcLAEIwHz7prlKS2f/n6++YKLo7Q3z57+vF187ahT5WQ7+76WtZKV/cuUPoOkGOV47Ty/ezTNv7KLfF+G8S5/nnZWNjMhz8fizm9m6u5vvLZzApMpszjqujHOOL+fKCyby8tJa7np4Hd85exxnHFfGRWdWUFnm5dKzKvEHotz3z43YrDItnSFOvPQF1m1pZeP2Du786zqyvfYDKpvXY+ed1S10dYf41pnjWPphPa8vq5f+9+pZRiCk3TJzfGkuB7ErOFgCkAHj9Du3fbNqTO4R3zlrvH7tHz+UM9IdnHVcOX99fis2q7LPAOvTMEywqjJvvl/P9KkFfO+CiYTDMUbkunn49hNIT7Pylyc3csysIu59chMnzimhINtOfzCGzSYhMLjo6xU8/vwOykZmsG57F5t3d/PY3acxcWwWkVCM0+eXccm5E3ljWSOxuI4sH1jvqekG6W4Lf31pK1Mn5DOuooCb7lslHVGVa5w8r8S7ZnvXDSJhSByU7vhgXFQA3HTxXOvN/7dm82O3HF8Wi+vmFb96U/rRxdPxBaM8tWg3mem2fZw8n3lSITAMA5dT5c6fH43NY6d2Zzurt3ZQVealON/N2OI0vF47ug66YeB2WhESBAIxACyqgj8Yo6apn5qmfrbX9VGc62T85ALSFcG1dy1jd0N/Qpyf0PQPLc+AqSpJAn8wxqxJ+cybUcQNd73H9y+cbH7z1LHmCZe+FC30OsftamysZ28g67BxMASgAJrV6v12RZnnr0/eeYJ+0hUvy6oq84PzJ/HbB1ZitSiDNw8SNxPY5739kZiwMQmFY1x23gTOPqmMklwXkbjJnhYfbV0hwpEYkqwkHDmGiRADbl2BaRqoFoUMt4WRI9JIc1lo6w7z7w+a+P1j64hrRsL0+4zKH1rugTLLsqC3P8q135vGu6v28OG6Zj74+znaHY9vUJ5+Y9e96P4fmQchhuBgeAJ107xJEsofrrps4Xjz3dXNNDT18IvLZvHO6iaiMQObdd/Q7KE38tMwTbBaJDRdZmK5FwOJ5xbXYHVasKkCPaoRjpn0+v34fFHCEQ0TE5tVIc1lIz3NgsOqE4kZNPXGCPYHKS/xMnl0JqoioSjyAVd+ojx7jzUME6tF5rV36jj7+HLeWdnIoy9uly85s8J8aWnthdPGlv9mWSKGIOnXHB6GWwAyoLvddx9dWuSZMndagfHNXyyWS4ozyc6w8ehzraS5LB+7yaZpDorgs8RgmiAQPL24hm/ZVIJRnXU729i6q5M9bQGCER1dN0AkjjNNc9CzKMsJ509hjpOK0dlUlXnwBWIsereBUETD7Uz4Ig5EjPsrl8OusGV3NyfPLWXuzJE88dpOceV5E7QjjyhIf39l03nAvcl7NGxBJMPeAggBgYB+0SVnlVC3x2ds2t4hXXnBFNbv6CIc1bBZZT7a9ZvmUNevOdglDPz90WOjMZ3dDb3c8KcPqW/oAyFQrAp2q5yIBFIkNM3AxEBVZexWBatFHgwO3d3Qz+ad3WBojChMx+2yEo7qaFoYi0XBapE+unjkgDCMhOfyvdV7mDutkLc/qGPpqiaxcEGZ+fbyxotM07xPCPGV7QIEoJ925Fj3orVtp54wu4jn3qqR7Q4LpQVuHni2AZdD/Zhdvb8n3jRNJEka/H0ommbwrTMqyMxwoIrE0y0rChYFwlEdTBNFkfF6rHT2R9hW08fmnZ00tfpwO6143BYuPWc8qiKwW2XaukI47AqqIqMj2LSjk3dXNWP/D6yUoeV22FU27OjghDkjGVmcwZOv75Lv/sUcMyfLNTXXmzse2MyQGMj/NsNpBkoAr61sPbKiLDN3RJ7beOODJjF1fB49vihtnSFU5ePF+WgFCyE+sfIhMaBbt62TV5bWUFGaTixuIoRJUX4az71ZzbtrWnhrRSMrN7cyY1wO5504mhuvmMG3Th1LMBQjGtNZsryRJSuaOGpyPnVN/Rw5KZd+f4SX3qqhtrEPVZE+VzcAA95LnZ21PcyenMeaLR3optBnT8mXOnoDJw29V8PBcApACEDX9QVHTck3G1v8RmtrH1Mqsthc3YUki/+oWTWM/ffFQgjq9/jYsrubHXW9ZGXY8ThVdtT0sK22h201vWze1c2zb9Zy7k8W0dHuY93mPZw2fzTfPns8Hd0hdtb3sq2ml9pmH5WlmQRDyW5hVydtXSFkSXzuUZphmtgsMpt2dVFZlokWN1i/o1vMm1EIQpqf1PawmYLDKQBdSszKHTVzfI5YvqlNyKpCXqaDXfV92C0H1qQmBm2ffn+sFhmHTcVuVZCFjizAZpGx2xTstsTPHK8DhMTi5Y3MnVHMovcbOHP+KHIyHaiKjM0qoaoyFouEKoPdqmC3KajJeMNPQwixzzhl3/KDRZVpbPOjSIKcHBdLVjRI40o9OBzWI6aUjPKQEMCwmOjDJQABmGW5o7Pcbvu4knwHKza2SiPy04hpBp09kf02/5+XgUGjaYIkJEyRDMEx977imo7NItHaFcFqtaAqglAgyqgRaYQjGhICM1mJhmlimMbgZz/1iyYr/5MEAMmJolCczr4wlaO8rNnWKTLS7OaIfFfWxsbOccnDhqVuhksAEkBtZ+vo/ByHx2FVzR11vWJ0kYfuvggxTedT7tfnYO/JhCyhqsrguGF/GIZJPBYj0UIlwsKFEEmDPDHf+2kV+lGGWi37/X+yhM1tfspGuGnpCBEJR/XRRR40zRwQwFeuBUDT9PLSQg9x3dQ7eiKMLEyjrSuYGOl/qZfbezZd1zA0/WOuFUkI4lpiIimuaeiGicNpoaa5H5tVxjAZbEUEJNceH8CVB1ufT/NVmKiqzJ42PzmZTrRonOaOAKNHZgBGxZf7MHw6wzYGSH6nkuKCNHr8cfS4QWaGk86+KIr0nw0ADwRJEghpIOmH2Od5EsmQrkAozjHTR7BueyenHlvGi29V09EdQpETt0USEmLgg19iAU0TFFnQ64/jsKsIWaK5IySK8t2AKBm44pd2wU9h+ASQ+Fb5uZlWOnqCIAR2q0SfL4ysfLneT0kSBIIxQuEYcjJ8W4trGMk4Pt0wkWXBjy6YyIgcO9leB2+v2sPfX9pBRpoteZyBPqRr+rKn62RJwh+MIgmwOyy0doXI8dpBkrKT3c2wCGC4HEEDXybH41Tp6gkJIUvIkiAYjifMqi/h6wqR8Lb1+2McPa2AmZPyEokgTAjHTExJxmFPTARVlXs5ce5Iaup6uPOR9bzyXj3xIS5Ik2QzPjio+3JrRJIS/gAzGdTS1RcRLruKLEtZWswQQogBS+C/KoTh8wQKwJScDpvKno4AigyYBvG4cUADrAOZETQM0HWDay+dRp8vSltXhOr6fhRZ0B/Suf+JDaR7rBi6iWGaZNxj4cLTKjlxTjFTJ+SxaVcnT766E4ddRZIkJFlC13R0w/gvDMkSi1d03cSiSgSCMayqQJGR4dfDNiE0fH4AE5Ak02JRMEyQZSm5WJO9/ewXQJIEoXCcH1wwmcZWH3c+tII97QF0w8AUMroO/lCcYEgjEIoTjRnUNPv56a3vsGx9O77+ILMm5PHrH80mGEqsH0hMEw9kjvr8ZdufWShI+jRME1mSiOs6Ap0vfTz8GQyfAARg6InVuckmf3CEfQB82shaCEEwFGdKVQ6qIvO3F7aRlu5ElQVKcnXwwGyfIkvIskRvf4TiPCcnzi3jydd3UlacydrNbVSNSuf0+aPo8yX6Z0mWE4PJL6DRTyq7ECCS7yuyDOKznUxfNsMcEqYboVAMqyLQdANJTszMfV6/+gCSgJhmML48k5UbW7BZVQzDSAz4NJ14LIZpGoOj/1A4znWXTueH35yI26nQH4iyYWcnU8bnsXpzO6fOG4UqSyAJRNIc5DPE+lnOn49iQjJXgURcM7BZFOIa6MbwBukMnx/ABBCdvlAcr9tu6loiEYPNmgiy+KLfWpBwAQfDcRI+H4GQE/24JMtIItHqGIbJk78/iRF5Ln7xhw95c3kTiizR1h3G67HjD0RxWsGbbiMe1zFMI2kCml/q02maJqqSSB0QjMTJSLOawYiGrhl+Rf7NsAwAYRhbgGR0XEd3f5ycbAcYBpGYvncK+AsqwMQkENLITLejDY7mTWRJRlYUJFki5I/wy+9Pp7jAzfd/uxSHTcXjsiSaaENPvMzEeEKWxaDZmLAEPv1WfZbz56MYhonNIoGAcEQjx2ujzx/FNMyOpNS+Uq7gATOvsaUjSG6WEyHLBENxsjMcaPqBWQIfZaDZNUywWRQ27upk+rgcDMMYNAk1XUeWBFHNID/fzfEzC/n9o2tQFBlFFhhGYiCam+kkEIpjt6loukS/L4okEtb/gEv4y2qbhUhEC2d47OiGhBbTKcr3mC0dITDN5uTT8pVyBZsAMlJtbVMfVlVIaW4Le9oD5Hnt6F+gCxgQjt2msHV3N75gnIUnjMHfH0os5ExePRzRqCj1EAjFqG/xo8oDvRKosmDa+FzWbW9nQnkGKza0EI5qqKqMZppYbSod3WEURfpSGmWBIK6Z5GU66OkLAzAix0l1cx9g1nzZXtFPY1gF4Eyz7Wpu88d1zZBKC91m7R4f2VnOQW/df3zSIX53wzBxOVUefHoTk8bmcP6plfQF4gQiOrLQsShgtahEYmCSaDnimkFzi48LT6+koztAVoYdt9vKQ89soaQwDUmSBruB2mYftgOcsv4shEj4K/KzbTS09ON2W0h3q6K6oQ9ZlreaQ+7Zf5thFcCd3yhu7O6LNLT3Rpk2Ls+s2+PH47YmMnn+B9G2+5x4SIVIAiRJ4oa7l2GzqaQ5FDp7QzR2hGjY46OlI0jcMMnxOojFExNBv/7RkZx+bCmSLCgpSOPHt71PMKxTWealszdCQY6Dzbs66ejZf8TS570ZqipRlJfG9vo+qkalm7puyPV7fLEsl2PrkMP+6wynK1i+8uG1ccN0rd1a21d+1BH5xiNPbZJC4TgjC9xsq+nBZpW/kEs44VgyuOTr43A4FKwWlfNOKiQYNynIcTFlQgGabnDBKaOYM62AqRWZGMDiZY1s3d3F26tbkgGiEtPG5dLW1s8R43K45o5lpDmtCY/gl0BcM8jNdGCzqdQ3+TjroslmfWtQdPeGd+rxaxqEuHnYFogMa1CoYYIkyUuXrWs575YfzMDmUNle28P40Zms296Jw6agf2GfgMRbyxuwWRWiMYO7/7Eeqypjt1sIhmNUlaZz9/Xz+PeH6/jJ/76H3aaASFzT5bDQ1hng+KOKycqwUVKYxn3/2kxHT5Q058cDVuHA1ywMlk9KJK6qKvPS2hEkHtU4elqBsfjDJmFo2nuSdLPBMOYXHE5HkAGQmZm2ZO2WtlgsFldmTswxV2xsZ9QIDw5bwkX8RRECuvoiNLUF6OwJEYnq9AVitLT78QVivL26hWt/v4zvLRzPjT+YwYh8Fy6HBbtVQZJMLj9/MndcN49YTOdP/7eJDze0kebaf+XvveaBj2EEiQijSWOzWbmlncICN4W5TuntVc3CYrEuGoh+/6L34UAZzhbAAKSe7uYa3XCtXrO9a/a5J441fvDrJXIwFGdqVS4rN7Xi/EjWjc+DIkuDeYMGSQZyelwWXn+/gc27uzn3lDFcdm4VgbCOaZikuSy4PXZu+ctK3l7eSEwzEk/+Z6xRPNAWQCQjgstGpOGyq6zd1MalC8eZze1BaWdtT/tJ0/Lee/nDXhjGoNDhXhgi6YZpSApPv7Ck9qh7rp9rZnidvLu2hQmjM1m+oSWxVk/snR7ed43gwHt7/04sCk0azkNmDAeijMzBuYeEO1c3TNLdVnr6Y9zx0FocdgVvuh1VlvAFY/T0hZEkgcdlxWpRBpeAS0Ikp4j3lmPg2tLAdRP2xWA20oHrQzJABYjGdCaOzWHV1g50w+CcE8r1p16vVuJR4+VXlu/0M8zrA4dbADpARaH36RWb2n7X2Rt2LTy+zPzbyztEXXMfLqeKppuEo1rCSWMmonkHP6wnTDJVlQaTQ0Vjibw8pmkSi+uYgEWRCIY1ZCmxbDwQimNVZRQlOQmFwDANnA4ViyrT3RshruuJsYJNwW5VicQ0NN1ItEiGSTiqI0mJiN6B65imic2iEI4mumtJSsxxOGwKwUgizsFmTaSyC4biqKqE26ny3tpm+n0x5s4oJjvDIb36Xr3p9Toe7enxD3N1DH9+ABOQtzc2tEWi+rN/e3GH+PYZFbqqSMnKTeT3nTMln8pSLxNGewefIMMwcTstFOQ40ZMhfkW5bo4+Io9QJI4JVJZ5GV+ehSwJZk/Kp6osE8M0OfqIAnK8DnTdTE4IGYwpyWDmhDwkAZWjMjh6SgGlBW5mTszDBMaMTGdqVTaBkIaqyEwdl8vo4nTCkTilhWlMGZtJZakXXTeZUpHF5IpsRhd7mD4uF00zmT4ul7IiD4FgDJtVZtakfAqyXRiGAFMQjsa57Jwq/dV36kVLW2B5f1/HymR9DOvSsIOSIMI0odSb9scXltRosiJLZ35tFH3+GKoq0e+PctU3J2GzKowblcHPLp5MfyBGNG4wa2IuN/9gZrKFkOkPRLn9x7O55OvjaGsLUJTrpDgvke3z4tPHMKY4HZfDQnG+C18ollhVJAT+YJzxZRlcdPpY2tr8VJVl8J0zK9hR34fboeJ2qERiOo/+Zj7zphewpyPImOI0FFli1sQ8Joz2snFnF9PH5+APxpg/YwQnzylmW20PeZl2hEhE+Tx5xwkU5bvo7A0zqSILi5qY+QxFNKZUZjOlMpOHn90iPA7lruQgc9jr42AIQAfkus7mzf5A9Pk//X299JOLJ+uynBghx+IGfYFYYjLGFDS3BwHwuK00tgVQFcH4ci+hSBzdgP+5ZyXnHjeKo6fns25bF01tAXSgvTtEVoYVj8vC04uriUQ1pCGpOPyBGL19EXTDpM8XIRCKk+62sLO+l87eEH3+KDfcs4JfXTmT0gIX67Z30NIVwu20cOEpFWR4bPz1xe0gCXp9UUKhGB6XlTXbO9EMg2213fz5Hxu474ZjsSgy67Z1JEUu4w/GuPHS6fqzb9bKdU196/sem/8yQza8Gk4OVooY0zQRo0d4b3r+rdpod19E/PD8SWZnbwRrcgVvjteG3SoPrhnIz7KjSIKdtd2ccsxIfP4oLodCry/C1be/x+3XHEVhjpNwVEdRJULhOGfMK2XBrBH0+6PYLPJeo0CIwbn4gZg/m1VmwuhMykZ4CITiZHpsbNrVwx2PrOKBX81DN8HtVHnt/QZeWFrDP39/MlcsHEcsEkdWwOVUmT4ul7xMO8FQnIIcFy+8Xc+SlU3ce+NcevrDqGoiEOWkOUWUjHBxzz83kud13SDOfUbnIKWIOVgCMABpV0PDDkUSf7rhnpXS5edU6KOL0wgE4ygy1DT5eOL1nVy2cAIOq0xWuo32njAvvdPArIl5uJwK0bhOfraTVZs6eOTFHdxz/THouoYWN8jMcPCXZ7YxpTKHK84dT3tPeDDB80CQpxgI9wKiMYNF79azYWcXJYUeYnGDkflunn69mlVbOvnTL46muzdM1Sgvj72wgzOufInjZxfhSbNhGtAfiPP84mraeyLkZ7vQdZOiPDe/fWA1pm5w/aXT6e6N4LAr/O6qI/VbHlkr9/RGXu3oblvEQdxd5GCmiTMA6eJpeb9bvbm95uHntir3Xj/HsMiCWNygINvB8bNH8uDTW8hMtzNxTCY9/RF2N/QTicQ4+ohCPE4LFSUZjMh38c9Xd/Lcm7vwemzYrQpIAqtV5id3vM/Jc4qZP6OQWNxASiaXhGQ8oiRwOSxIkqCiLINT55VSkO0kL8vB6JFpZGc7uevx9azd1oHNqlCc7+Jbp42lINvJP17dSTyuY7dbcDpUKsszOG1uCS6HSmmhm/KiNDxuKzfeu4ruvgi+YIzbfnykubWmSzy7uNp/RGnuVcmJ0OGOBBvkoCeKBPSRhYXHdvSHl75232na+u2d8i/vXS5KCtOIRHW6eiNkeCyoikQ4ktjMQZYTCZ81zcBqkQlFNTTNIBrTsVkT0T8WVUaSEulhhQTeNBt9/hiyBF6PjTlT8olrOk8s2k1BthNdTySLkCVBny+KzaagyIJQWEfTDWJxHafdQlzXycmwA9DaFURVZOxWKbnqN2Ey+kNxnPaEhR2KaEhC0NoV4sJTRnP996Zpx373JSUa1q7o7u14kIO8t9DBFgAk/d4ed/ZvMjNtv3zr4dO0n/3+A+Wlt+vJzXQACXs/MYIfWNw54AkC00g6WcRev7wJmAM7NyWXnWu6kUjyoJucc9womjsCrNrcsc/5Ej6CxD6CA3sDSMnk0MBgVFAsnkj0rSry4FQ0DEQ4g8Uio2mJxSUWi0QwrFNe7OGVe0/WvvGzN5UVG1qfi0f7zzFM86DvKXQoCEAAsiwJTbVmLJo1OffEp35/onbWj19XNm7vIsNjA0z8wRhWi4IsiX1cxR9tPweihEzD2G+7KkkSoUjCSTR0enfgPEPPN/T3vZnEBryO7P07KTqRzDsUimiDuY5CEQ27VWLZP87V73h0rfzws1u3n3fsmFn/fGNVIHnqYU0L91EOdrJoIJl23zDFWVMLv7lsXeu2n9z5gfLMH07Sy4s9tHeHqCz1ctWFk4jFNaIfSdL4SZ3nJ1U+gNOuJHL+7+d4cz/vwUdaHhhcPjbQ4kiSwETQ64tw4WljmHNEAT2+KKoi8cZDZ+hPvLpDfviZLd1VpRlnDtlo8qBWPhwaAoDkw/fEss29s8Zkn/bU67sbb7pvpfzq/afpE8dmsWRlMzVNPn5z1WwyPFZ6fdHBBZwfO9EBrMzVP0emr6HHf/SzipxoVXTN4IYrZmGxKLywpJoMt5XFD51uvL1yj/zr+1cFR+WmnblpR90u9u4kdtA5FLqAociAPrmqvGpzdefii8+sHHHLj2dp3/6ft5TF79bytaNHcfb8El55u4531rSS5lIZcCMfDAYWuPT2RxhX5uXir1fx4cY2/vXyTipHp/PSn0/VX1haJ9949/JgUWba6bV7GpdyiO0leKgJAJIimFlZOXpNdeuiU44tKbv/l0drdzy6Trnn8Q2MKHTzw29Oxh/W+PuLW+nui+JxWwd38RgOBhJJ+INxrBaZM+eXUlGSzj9f2826TXs466QK7rvxGO3WB9co9/1rW19pgfPM6vrmdznEKh8OTQFAUgQLpowteG9bx1NV5Rlz/vq7edq2un756luXia6uEGefOIp5M0eyfH0rb37QQDiq4XJYUBSxz+5eXxYD09SGmcgrIAnB7Cl5LDiymJpmP48/v5VYXOd/r5ltLjyuVL/qtg+VV5fW7q4q8i7cWl+/kUOw8uHQFQAkRXD3j060Xv/YqntsNuWyO39+FLOmFeq//MOH8nOvbyMvL4OFJ5QxstDN+u09vLOykZ7+CFarkojwGWI2fh497K30xDx+OBInzWVl+oQ8Zk3MIhjWeObNGqprupkzs4Q7fnak3tcflq+6ZRkNLf0vz59eeukbyzZ0cpBt/U/jUBYAJBMmCgE5WbmXdPdH7zpjQan3xu9P06sbfeKWv6yRNmzeQ2lJNicfM5LifBetXWFWbmilurF/cJcwiyqjKtJgUAZ8xHQc8rtJYoSv6yaxuIGWjBMYWejhiKosRo9Mpy+g89o71Wze1kpRUSbXfm+KMX92qfngk1vkB57cELWryk0+f9ftyS7pkK18OPQFAOzdNn5ceXnZ9vqOO7O89q9f852pnDp/pL5s9R7x4JNbpQ2bW/CkO/nakcVUlqZht1tp7QpQ29hPc1uA7r4IobCWzPW7N6oH9o0wSuwirpCZbiM/x0npCA/5XhuKqrKjrpclyxtobw9QMtLLd8+pMM5YUGas2tSh3PbAauqafe+W5Ht+WtPYuDZZZpOD6OY9EA4HAQwgA7okICs7/8yu7uBNo0vSJ19+4USOParY2Lm703zqtRpp0Tu1IhKKkZfnoao8nTElGeRk2pElCU1POGYCwSihsI5hgImBLAnsNgWX04rDllgyphvQ44tQ1+Rjy84uGpt9yBaZo6cXmuefUm7MOKKQzTt75HsfX8vaLV01Lof11oC/49HkU39I9vf743ASAOz1WxgPPjhVveaaugtCkfhV5SXpU846voxTFpSjCl1ft62HN9+vl1asbxEdXWEQEm63hZxMO1kZdtLdiShgVRHJbeMTS8f6AjE6e8K0dwXx+aJgmnjSbUwbn2ceN6fYOHJirmlxWZV3PmjgX6/uYuvunmow/7JgcvYjb6yq9jGYkerQsPEPhMNNAAMM9qvm0wvltIv/fbI/on/H47EeP3V8juPEY0qZUpGBx20xevoixq7aXrGtpl/U7ukXbZ0hen1REQprxOKJhBWqKuOwKXhcFrMgx0FJQZpZMcpjVozKNLPSrVJMF9LWmj4WvVvDig1t8c6u8Hs2q/y3ixaUPffQq2tDHy3T4cThKgAYMjaAxLKwETm5pY2d4ZMx9JOdLtvMUUWezIljvYwf7WVUUQZZGTYcNglZEiamiW7opomJJCQhSTKmiQhHdLr7otS1+Ni6u5vNu7rZ1dDn9/WH12Gai7xe28v9fb3bh/gcDpltYD8Ph7MABhgQgkmy6ZUkGDUqL7uuLjRZ141ZYE6SLHK506YWOOyyx+2wWJwOC2pyTkHTDUIRnWA4rgVC8f5AKN6qx7QaYBOyunqEx7WupW/PniEbWQxc85DZBPrz8lUQwFAk9laMAclOOTlVPLmk1FO9p9vbr5uZaKYCsgVMBYwIaHGrVe0dk5veva25qXcgS+iQ2hXs9eEfNn38Z/FVE8BQBp7SgVnd/7R/lod8drB1+arxVRbA/hBDXvvD5DCw3VOkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKVKkSJEiRYoUKQD+HymDTDMaBmfDAAAAAElFTkSuQmCC' style='width:44px;height:44px;border-radius:50%;background:#000;border:2px solid #c8a44a' onerror=\"this.style.display='none'\"><b>BANK JENSEN</b></span>"
    nav = f"<div class=nav>{logo}<span>{(user['username'] if user else 'GUEST')} <a href='/logout' style='margin-left:12px;color:#ff6b6b'>Logout</a></span></div>"
    return f"<!DOCTYPE html><html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Bank Jensen</title>{CSS}</head><body>{nav}<div class=container>{content}</div></body></html>"

@app.route("/")
def index():
    return page(f"<h1 style='font-size:36px'>BANK<br><span style='color:#c8a44a'>JENSEN</span></h1><p style='opacity:.7'>Private Bank Sultan Digital | Aman | PIN Protected | Elit</p><div class=card><div class=grid2><div class=stat><h2>100+</h2><small>Nasabah Sultan</small></div><div class=stat><h2>PIN 6</h2><small>Secure</small></div></div></div><div class=card><a href='/register' class='btn btn-gold'>BUKA REKENING GRATIS</a><a href='/login' class='btn btn-outline'>LOGIN</a><p style='text-align:center;margin-top:12px;font-size:12px;opacity:.6'>admin / admin123 + PIN: 123456</p></div>")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip();p=request.form["password"].strip()
        conn=get_db();user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone();conn.close()
        if user:
            if user["is_blocked"]: return page("<div class=card>Rekening diblokir admin!</div>")
            session["user"]=dict(user)
            return redirect("/admin") if u=="admin" else redirect("/dashboard")
        return page("<div class=card style='border-color:#ff4444'>Salah!<br><br><a href='/login' class='btn btn-outline'>Coba Lagi</a></div>")
    return page("<div class=card><h2>Login Bank Jensen</h2><span class=badge>PIN Protected</span><form method=POST style='margin-top:16px'><input name=username placeholder='Username' required><input name=password type=password placeholder='Password' required><button class='btn btn-gold'>LOGIN SULTAN</button></form><br><a href='/register'>Belum punya rekening?</a><br><br><small style='opacity:.5'>Demo: admin / admin123 + PIN 123456</small></div>")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"].strip();p=request.form["password"].strip();pin=request.form["pin"].strip()
        if len(u)<3 or len(pin)!=6: return page("<div class=card>Username min 3, PIN harus 6 digit <a href='/register'>Balik</a></div>")
        acc=f"{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        try:
            conn=get_db();conn.execute("INSERT INTO users (username,password,pin,account_no,created_at) VALUES (?,?,?,?,?)",(u,p,pin,acc,datetime.now().strftime("%d %b %Y")));conn.commit();conn.close()
            return page(f"<div class=card card-gold><h2> REKENING JADI!</h2><p>Username: <b>{u}</b><br>No Rek: <b>{acc}</b><br>PIN: <b>{pin}</b><br>Saldo: <b>Rp 100.000.000</b></p><p style='font-size:12px'>*Ingat PIN untuk transfer!</p><a href='/login' class='btn btn-dark'>Login Sekarang</a></div>")
        except:
            return page("<div class=card>Username sudah dipakai! <a href='/register'>Ganti lain</a></div>")
    return page("<div class=card><h2>Buka Rekening + PIN</h2><p style='opacity:.7'>Dapat 100jt + Buat PIN 6 digit</p><form method=POST><input name=username placeholder='Username' required><input name=password type=password placeholder='Password' required><input name=pin type=number placeholder='PIN 6 digit (contoh 123456)' required maxlength=6><button class='btn btn-gold'>BUKA REKENING</button></form><br><a href='/login'>Sudah punya?</a></div>")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC LIMIT 8",(user["username"],user["username"])).fetchall();conn.close()
    session["user"]=dict(user)
    tx_html = "".join([f"<tr><td>{t['created_at']}</td><td>{'IN' if t['to_user']==user['username'] else 'OUT'} {t['from_user'] if t['to_user']==user['username'] else t['to_user']}<br><small style='opacity:.5'>{t['note']}</small></td><td style='color:{'#4ade80' if t['to_user']==user['username'] else '#ff6b6b'}'>Rp {t['amount']:,}</td></tr>" for t in tx]) or "<tr><td colspan=3 style='text-align:center;opacity:.5'>Belum ada transaksi</td></tr>"
    return page(f"<div class=card card-gold><small>{user['account_no']} | {user['created_at']} | PIN: {user['pin']}</small><h2 style='margin:6px 0'>Halo, {user['username']} </h2><h1 style='font-size:32px'>Rp {user['balance']:,}</h1><span class=badge style='background:#0003;color:#000;border-color:#0003'>Saldo Aktif | PIN Protected</span></div><div class=card><div class=grid2><a href='/transfer' class='btn btn-gold'> Transfer + PIN</a><a href='/topup' class='btn btn-dark'> TopUp</a><a href='/qris' class='btn btn-dark'> QRIS</a><a href='/history' class='btn btn-dark'> History</a></div><a href='/ganti-pin' class='btn btn-outline' style='margin-top:8px'> Ganti PIN</a></div><div class=card><h3>Transaksi Terakhir</h3><table><tr><th>Tgl</th><th>Detail</th><th>Nominal</th></tr>{tx_html}</table><br><a href='/history' class='btn btn-outline'>Lihat Semua</a></div>", user=user)

@app.route("/transfer", methods=["GET","POST"])
def transfer():
    if "user" not in session: return redirect("/login")
    conn=get_db();me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    all_u=conn.execute("SELECT username FROM users WHERE id!=?",(me["id"],)).fetchall()
    msg=""
    if request.method=="POST":
        to=request.form["to"].strip().lower();amt=int(request.form["amount"] or 0);note=request.form["note"].strip() or "Transfer";pin=request.form["pin"].strip()
        if pin!=me["pin"]:
            conn.close()
            return page("<div class=card style='border-color:#ff4444'>ERROR: PIN SALAH! <br> PIN kamu: "+me["pin"]+"<br><br><a href='/transfer' class='btn btn-outline'>Coba Lagi</a></div>", user=me)
        target=conn.execute("SELECT * FROM users WHERE LOWER(username)=?",(to,)).fetchone()
        if not target: msg=f"<div class=card style='border-color:#ff4444'>User {to} tidak ketemu!</div>"
        elif me["balance"]<amt: msg="<div class=card style='border-color:#ff4444'>Saldo tidak cukup!</div>"
        elif target["id"]==me["id"]: msg="<div class=card style='border-color:#ff4444'>Gak bisa ke diri sendiri!</div>"
        else:
            conn.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,me["id"]));conn.execute("UPDATE users SET balance=balance+? WHERE id=?",(amt,target["id"]))
            conn.execute("INSERT INTO transaksi (from_user,to_user,amount,note,created_at) VALUES (?,?,?,?,?)",(me["username"],target["username"],amt,note,datetime.now().strftime("%d %b %H:%M")))
            conn.commit();conn.close()
            return redirect("/dashboard")
    conn.close()
    options = "".join([f"<option value='{u['username']}'>{u['username']}</option>" for u in all_u])
    return page(f"{msg}<div class=card><h2> Transfer + PIN</h2><form method=POST><label>Ke Username</label><input list=userlist name=to placeholder='Ketik username' required><datalist id=userlist>{options}</datalist><label>Nominal</label><input name=amount type=number placeholder='100000' required><label>Catatan</label><input name=note placeholder='Buat makan sultan'><label> PIN 6 Digit</label><input name=pin type=password inputmode=numeric placeholder='Masukkan PIN kamu' required maxlength=6><button class='btn btn-gold'>KIRIM + VERIFIKASI PIN</button></form><br><small style='opacity:.5'>User: {', '.join([u['username'] for u in all_u]) or 'Belum ada'}</small></div><a href='/dashboard' class='btn btn-outline'>Kembali Dashboard</a>", user=me)

@app.route("/ganti-pin", methods=["GET","POST"])
def ganti_pin():
    if "user" not in session: return redirect("/login")
    conn=get_db();me=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    if request.method=="POST":
        old=request.form["old_pin"].strip();new=request.form["new_pin"].strip()
        if old!=me["pin"]:
            conn.close()
            return page("<div class=card>Old PIN salah! <a href='/ganti-pin'>Balik</a></div>", user=me)
        conn.execute("UPDATE users SET pin=? WHERE id=?",(new,me["id"]));conn.commit();conn.close()
        return redirect("/dashboard")
    conn.close()
    return page(f"<div class=card><h2> Ganti PIN</h2><p>PIN sekarang: {me['pin']}</p><form method=POST><input name=old_pin placeholder='PIN Lama' required><input name=new_pin placeholder='PIN Baru 6 digit' required maxlength=6><button class='btn btn-gold'>GANTI PIN</button></form></div><a href='/dashboard' class='btn btn-outline'>Kembali Dashboard</a>", user=me)

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
    return page("<div class=card><h2> TopUp Sultan</h2><p><span class=badge>Bonus 10% jika >=50jt</span></p><form method=POST><label>Nominal</label><input name=amount type=number placeholder='50000000' required><label>Metode</label><select name=method><option>BCA VA</option><option>GoPay</option><option>OVO</option><option>QRIS</option></select><button class='btn btn-gold'>TOPUP SEKARANG</button></form></div><a href='/dashboard' class='btn btn-outline'>Kembali Dashboard</a>", user=me)

@app.route("/qris")
def qris():
    if "user" not in session: return redirect("/login")
    u=session["user"]
    return page(f"<div class=card style='text-align:center'><h2> QRIS BANK JENSEN</h2><p>{u['account_no']}<br>{u['username']}</p><div style='background:white;padding:20px;border-radius:16px;margin:20px auto;max-width:280px'><img src='https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=BANKJENSEN-{u['username']}-{u['account_no']}' style='width:100%'></div></div><a href='/dashboard' class='btn btn-outline'>Kembali Dashboard</a>", user=u)

@app.route("/history")
def history():
    if "user" not in session: return redirect("/login")
    conn=get_db();user=conn.execute("SELECT * FROM users WHERE id=?",(session["user"]["id"],)).fetchone()
    tx=conn.execute("SELECT * FROM transaksi WHERE from_user=? OR to_user=? ORDER BY id DESC",(user["username"],user["username"])).fetchall();conn.close()
    rows="".join([f"<tr><td>{t['created_at']}</td><td>{t['from_user']} -> {t['to_user']}<br><small>{t['note']}</small></td><td>Rp {t['amount']:,}</td></tr>" for t in tx])
    return page(f"<div class=card><h2> History {user['username']}</h2><p>Saldo: Rp {user['balance']:,} | PIN: {user['pin']}</p><table><tr><th>Waktu</th><th>Transaksi</th><th>Nominal</th></tr>{rows or '<tr><td colspan=3> Kosong </td></tr>'}</table></div><a href='/dashboard' class='btn btn-outline'>Kembali Dashboard</a>", user=user)

@app.route("/admin")
def admin():
    if "user" not in session or session["user"]["username"]!="admin": return redirect("/login")
    conn=get_db();users=conn.execute("SELECT * FROM users WHERE username!='admin' ORDER BY id DESC").fetchall();total=conn.execute("SELECT COUNT(*), SUM(balance) FROM users WHERE username!='admin'").fetchone();conn.close()
    cards="".join([f"<div class=card><b>{u['username']}</b> <small>{u['account_no']} | PIN:{u['pin']}</small><br>Rp {u['balance']:,} {' BLOCKED' if u['is_blocked'] else ' Aktif'}<br><br><div class=grid2><a href='/admin/add/{u['id']}' class='btn btn-gold' style='padding:8px;font-size:12px'>+10jt</a><a href='/admin/block/{u['id']}' class='btn btn-dark' style='padding:8px;font-size:12px'>{'Unblock' if u['is_blocked'] else 'Block'}</a></div></div>" for u in users])
    return page(f"<div class=card card-gold><h2> ADMIN DEWA</h2><p>Total: {total[0] or 0} | Saldo: Rp {total[1] or 0:,}</p><a href='/admin/bunga' class='btn btn-dark'> Bagi Bunga 5% Semua</a></div>{cards or '<div class=card>Belum ada nasabah</div>'}", user=session["user"])

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
