import datetime
import json
import logging
import multiprocessing
import os
import subprocess

from flask import Flask
from flask import make_response
from flask import request
from flask import render_template
app = Flask(__name__)

process = None
queue = None
log = []

@app.route("/build_log_stream")
def build_log_stream():
    f = open("build.log", "r")
    log = f.readlines()
    log_len = len(log)
    last_line = int(request.headers['Last-Event-ID']) if 'Last-Event-ID' in request.headers else -1
    if (log_len - last_line) > 300:
        last_line = log_len-300;
    resp_str = ""
    if (last_line >= (log_len + 1)):
         resp_str = "event: empty\nid: log_len-1\ndata: \n\n"
    else:
        for n in range(last_line+1,log_len):
            # TODO(cbhl): filter out werkzeug events at the logger level
            if not "INFO:werkzeug:" in log[n]:
                resp_str += "event: buildlog\nid: %d\ndata: %s\n\n" % (n, log[n].rstrip())
    response = make_response(resp_str)
    response.headers['Content-Type'] = 'text/event-stream'
    return response

@app.route("/")
def hello():
    return render_template("index.html")

def build():
    logging.info("Starting build!")
    dt = datetime.datetime.today()
    revision = "0cryptkeeper%04d%02d%02d" % (dt.year, dt.month, dt.day)
    commands = [
        ["/home/cryptkeeper/src/ecryptfs",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs",
            "git pull"],
        ["/home/cryptkeeper/src/ecryptfs",
            "yes '' | make oldconfig"],
# TODO(cbhl): Turn clean back on.
#        ["/home/cryptkeeper/src/ecryptfs",
#            "make-kpkg clean"],
        ["/home/cryptkeeper/src/ecryptfs",
            "fakeroot make-kpkg --initrd --revision=%s kernel_image" % revision],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git pull"],
# TODO(cbhl): Turn clean back on.
#        ["/home/cryptkeeper/src/ecryptfs_userspace",
#            "debian/rules clean"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "debian/rules build"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git-dch --snapshot"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git-buildpackage"],
    ]
    for command in commands:
        logging.info("CHDIR: %s" % command[0])
        os.chdir(command[0])
        logging.info("SHELL: %s" % command[1])
        popen = subprocess.Popen(command[1],
                                 shell=True, bufsize=4096, stdin=None,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 close_fds=True)
        while True:
            line = popen.stdout.readline()
            if not line:
                logging.info("GOT EMPTY LINE FROM PROCESS -- ASSUMING TERMINATION")
                if popen.wait() != 0:
                    logging.info("PROCESS TERMINATED WITH ERRORS")
                else:
                    logging.info("PROCESS ENDED NORMALLY")
                break;
            logging.info(line)
    logging.info("Build complete!")

if __name__ == "__main__":
    logging.basicConfig(filename='build.log',level=logging.DEBUG)
    console = logging.StreamHandler()
    logging.getLogger('').addHandler(console)

    process = multiprocessing.Process(target=build, args=())

    process.start()

    app.run(host='::0',port=20349)

    process.join()
