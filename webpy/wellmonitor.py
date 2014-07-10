#!/usr/bin/env python

import web
import time
import arrow
import sqlite3
import send_email

urls = (
        "/", "index",
        "/update/?", "update",
        "/(.+)/?", "well",
)

web.config.debug = True
app = web.application(urls, globals())
DB = "../sensor_readings.sqlite"
ALERT_ADDRS = ["dane.t.larsen@gmail.com", "3037253982@txt.att.net",
               "beth.a.lammers@gmail.com", "3037757056@txt.att.net",
               "larsen@casinc.com", "3037728741@txt.att.net"]

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS sensor_readings (north INT, west INT, front INT, furnace INT, store INT, timestamp INT)")
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

def get_readings():
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC")
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


class index:
    def GET(self):
        render = web.template.render("templates")
        north, west, front, furnace, store, t = get_latest()
        t = arrow.get(t).to("US/Mountain")
        tstring = t.humanize() + " (" + t.format("YYYY/MM/DD HH:mm:ss") + ")"
        wells = [("North", "north", north),
                 ("West", "west", west),
                 ("Front", "front", front),
                 ("Furnace Room", "furnace", furnace),
                 ("Store Room", "store", store)]
        return render.index(wells, tstring)

class well:
    def GET(self, wellname):
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
            raise web.notfound()

        def fmt(t):
            t = arrow.get(t)
            return t.humanize() + " (" + t.format("YYYY/MM/DD HH:mm:ss") + ")"

        data = get_readings()
        welldata = map(lambda row: (row[idx], fmt(row[-1])), data)
        render = web.template.render("templates")
        return render.well(welldata, name)

def maybe_send_alert(wells):
    ok = True
    badwells = []
    wellnames = ["north", "west", "front", "furnace", "store"]
    for wellname,well in zip(wellnames, wells):
        if well == 0:
            ok = False
            badwells.append(wellname)

    if not ok:
        msg = "The following wells are overfull: %s\n" % (", ".join(badwells))
        msg += "The time is: %s\n" % (arrow.now().format("YYYY/MM/DD HH:mm:ss"))
        for addr in ALERT_ADDRS:
            send_email.send(addr, "WELL ALERT", msg)

class update:
    def GET(self):
        data = web.input()
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


if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
