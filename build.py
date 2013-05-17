import datetime
import json
import logging
import multiprocessing
import os
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
    dt = datetime.datetime.today()
    revision = "cryptkeeper%04d%02d%02d" % (dt.year, dt.month, dt.day)
    commands = [
#        ["/home/cryptkeeper/src",
#            "git clone git://github.com/zmanji/ecryptfs.git"],
#        ["/home/cryptkeeper/src",
#            "git clone git://github.com/zmanji/ecryptfs_userspace.git"],
        ["/home/cryptkeeper/src/ecryptfs",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs",
            "git pull"],
        ["/home/cryptkeeper/src/ecryptfs",
            "make oldconfig"],
        ["/home/cryptkeeper/src/ecryptfs",
            "make-kpkg clean"],
        ["/home/cryptkeeper/src/ecryptfs",
            "fakeroot make-kpkg --initrd --revision=%s kernel_image" % revision],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git pull"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "fakeroot debian/rules binary"],
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
