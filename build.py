import json
import multiprocessing
import select
import subprocess

from flask import Flask
app = Flask(__name__)

process = None
queue = None
log = []

@app.route("/")
def hello():
    while line = queue.get(False):
        log.append(line)
    log = log[-100:]
    return json.dumps(log)

def build(queue):
    popen = subprocess.Popen("git clone git://github.com/zmanji/ecryptfs.git",
                             shell=True, bufsize=4096, stdin=None,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)
    while True:
        result = select.select([popen.stdout],[],[])
        line = result[0][0].readline()
        queue.put(line)

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=build, args=(queue,))

    process.start()

    app.run()

    process.join()
