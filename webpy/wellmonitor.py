#!/usr/bin/env python

import web
import time
import arrow
import sqlite3

urls = (
        "/", "index",
        "/(.+)/?", "well",
)

web.config.debug = True
app = web.application(urls, globals())
DB = "../sensor_readings.sqlite"

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
        t = arrow.get(t)
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



if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
