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
    os.chdir("/home/cryptkeeper/src")
    popen = subprocess.Popen("git clone git://github.com/zmanji/ecryptfs.git",
                             shell=True, bufsize=4096, stdin=None,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)
    while True:
        result = select.select([popen.stdout],[],[])
        if not len(result[0]):
            break;
        line = result[0][0].readline()
        if not line:
            break;
        logging.info(line)

if __name__ == "__main__":
    logging.basicConfig(filename='build.log',level=logging.DEBUG)

    process = multiprocessing.Process(target=build, args=())

    process.start()

    app.run(host='::0',port=20349)

    process.join()
