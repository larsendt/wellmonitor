#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from wellmonitor import app
import os

if __name__ == '__main__':
    SOCK = "/tmp/wellmonitor.fcgi.sock"
    print "Running wsgi server (sock=%s)" % SOCK
    WSGIServer(app, bindAddress=SOCK).run()
