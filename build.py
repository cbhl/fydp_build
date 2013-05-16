import json
import logging
import multiprocessing
import os
import select
import subprocess

from flask import Flask
app = Flask(__name__)

process = None
queue = None
log = []

@app.route("/")
def hello():
    f = open("build.log", "r")
    log = f.readlines()
    return json.dumps(log)

def build():
    logging.info("Starting build!")
    os.chdir("/home/cryptkeeper/src")
    popen = subprocess.Popen("git clone git://github.com/zmanji/ecryptfs.git",
                             shell=True, bufsize=4096, stdin=None,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)
    while True:
        line = popen.stdout.readline()
        if not line:
            logging.info("if not line")
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
