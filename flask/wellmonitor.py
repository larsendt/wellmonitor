#!/usr/bin/env python

from flask import Flask, render_template, request, make_response
import time
import arrow
import sqlite3
import send_email

urls = (
        "/", "index",
        "/update/?", "update",
        "/(.+)/?", "well",
)

app = Flask(__name__)
app.debug = True
DB = "../sensor_readings.sqlite"
ALERT_ADDRS = ["dane.t.larsen@gmail.com", "3037253982@txt.att.net",
               "beth.a.lammers@gmail.com", "3037757056@txt.att.net",
               "larsen@casinc.com", "3037728741@txt.att.net"]

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS sensor_readings (north INT, west INT, front INT, furnace INT, store INT, timestamp INT)")
    c.execute("CREATE TABLE IF NOT EXISTS alert_log (timestamp REAL)")
    conn.commit()
    conn.close()


def add_reading(north, west, front, furnace, store):
    init_db()
    t = int(time.time())
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO sensor_readings VALUES (?,?,?,?,?,?)",
            (north, west, front, furnace, store, t))
    conn.commit()
    conn.close()

def log_alert():
    t = time.time()
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO alert_log VALUES (?)", (t,))
    conn.commit()
    conn.close()

def recent_alerts():
    now = time.time()
    one_hour_ago = now - (60 * 60)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM alert_log WHERE timestamp >= ?", (one_hour_ago,))
    results = c.fetchall()
    conn.close()
    return results

def get_readings():
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 100")
    results = c.fetchall()
    conn.close()
    return results


def get_latest():
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1")
    results = c.fetchone()
    conn.close()
    return results


@app.route("/")
def index():
    north, west, front, furnace, store, t = get_latest()
    t = arrow.get(t).to("US/Mountain")
    tstring = t.humanize() + " (" + t.format("YYYY/MM/DD HH:mm:ss") + ")"
    wells = [("North", "north", north),
             ("West", "west", west),
             ("Front", "front", front),
             ("Furnace Room", "furnace", furnace),
             ("Store Room", "store", store)]
    return render_template("index.html", wells=wells, tstring=tstring)

@app.route("/<wellname>")
def well(wellname):
    if wellname == "north":
        name = "North"
        idx = 0
    elif wellname == "west":
        name = "West"
        idx = 1
    elif wellname == "front":
        name = "Front"
        idx = 2
    elif wellname == "furnace":
        name = "Furnace Room"
        idx = 3
    elif wellname == "store":
        name = "Store Room"
        idx = 4
    else:
        return make_response("404 Not Found", 404)

    def fmt(t):
        t = arrow.get(t)
        return t.humanize() + " (" + t.format("YYYY/MM/DD HH:mm:ss") + ")"

    data = get_readings()
    welldata = map(lambda row: (row[idx], fmt(row[-1])), data)
    return render_template("well.html", welldata=welldata, name=name)

def maybe_send_alert(wells):
    ok = True
    badwells = []
    wellnames = ["north", "west", "front", "furnace", "store"]
    for wellname,well in zip(wellnames, wells):
        if well == 0:
            ok = False
            badwells.append(wellname)

    if not ok:
        if len(recent_alerts()) > 3:
            return
        else:
            log_alert()
            msg = "The following wells are overfull: %s\n" % (", ".join(badwells))
            msg += "The time is: %s\n" % (arrow.now().format("YYYY/MM/DD HH:mm:ss"))
            for addr in ALERT_ADDRS:
                send_email.send(addr, "WELL ALERT", msg)


def is_auth(auth_hash, counter):
    with open("auth.conf", "r") as f:
        key = f.readline().replace("\n", "")

    myhash = hashlib.sha256(key + str(counter)).hexdigest()
    return auth_hash == myhash


@app.route("/update")
def update():
    data = request.args
    auth = data.get("auth")
    counter = data.get("counter")

    if not is_auth(auth, counter):
        return make_response("403 Forbidden", 403)

    items = (data.get("north"), data.get("west"), data.get("front"),
             data.get("furnace"), data.get("store"))

    def try_int(s):
        try:
            s = int(s)
        except:
            s = None
        return s

    intitems = map(try_int, items)
    maybe_send_alert(intitems)
    add_reading(*intitems)
    return "acknowledged"


if __name__ == "__main__":
    app.run()
