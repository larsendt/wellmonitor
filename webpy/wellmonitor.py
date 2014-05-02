#!/usr/bin/env python

import web
import time
import arrow
import sqlite3

urls = (
        "/", "index",
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
        latest = get_latest()
        return render.index(latest)





if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
