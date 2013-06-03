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

@app.route("/trigger_build/lgkmGKfwyArYkONrLYo7bI7RgefbQRh2")
def trigger_build():
    build = {
        "kernel_full": True,
        "kernel_incremental": False,
        "userspace": True,
        "run_tests": True,
    }
    queue.put(build, False)
    return "OK"

@app.route("/build_log_stream")
def build_log_stream():
    f = open("build.log", "r")
    log = f.readlines()
    log_len = len(log)
    last_line = int(request.headers['Last-Event-ID']) if 'Last-Event-ID' in request.headers else -1
    initial_req = 'Last-Event-ID' not in request.headers
    if (log_len - last_line) > 1000:
        last_line = log_len-1000;
    resp_str = ""
    if (last_line >= (log_len + 1)):
         resp_str = "event: empty\nid: %d\ndata: .\n\n" % (log_len-1)
    else:
        for n in range(last_line+1,log_len):
            # TODO(cbhl): filter out werkzeug events at the logger level
            if not "INFO:werkzeug:" in log[n]:
                resp_str += "event: buildlog\nid: %d\ndata: %s\n\n" % (n, log[n].rstrip())
        if initial_req:
            resp_str += "event: buildloganimate\nid: %d\ndata: .\n\n" % (log_len-1)
    response = make_response(resp_str)
    response.headers['Content-Type'] = 'text/event-stream'
    return response

@app.route("/")
def hello():
    return render_template("index.html")

def get_snapshot():
    dt = datetime.datetime.today()
    return "%04d%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour)

def get_revision(snapshot):
    return "1cryptkeeper0~%s" % snapshot

def build_full_kernel_task(revision):
   return [ 
        ["/home/cryptkeeper/src/ecryptfs",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs",
            "git pull"],
        ["/home/cryptkeeper/src/ecryptfs",
            "yes '' | make oldconfig"],
        ["/home/cryptkeeper/src/ecryptfs",
            "perl -pi -e 's/CONFIG_ECRYPT_FS=./CONFIG_ECRYPT_FS=m/' .config"],
        ["/home/cryptkeeper/src/ecryptfs",
            "grep CONFIG_ECRYPT_FS .config"],
        ["/home/cryptkeeper/src/ecryptfs",
            "make-kpkg clean"],
        ["/home/cryptkeeper/src/ecryptfs",
            "make-kpkg --rootcmd fakeroot --jobs 4 --initrd --revision=%s kernel_image" % revision],
        ]

def install_full_kernel_task(revision):
    return [
        ["/home/cryptkeeper/src",
            "scp linux-image-3.9.0-rc2+_%s_amd64.deb cryptkeeper-test:" % revision],
        ["/home/cryptkeeper/src",
            "ssh cryptkeeper-test sudo dpkg -i linux-image-3.9.0-rc2+_%s_amd64.deb" % revision],
        ["/home/cryptkeeper/src",
            "ssh cryptkeeper-test sudo reboot"],
        # FIXME Actually wait for it to come back up
        ["/home/cryptkeeper/src",
            "sleep 60"],
        ]

def build_incremental_kernel_task(snapshot):
    return [
        ["/home/cryptkeeper/src/ecryptfs",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs",
            "perl -pi -e 's/CONFIG_ECRYPT_FS=./CONFIG_ECRYPT_FS=m/' .config"],
        ["/home/cryptkeeper/src/ecryptfs",
            "grep CONFIG_ECRYPT_FS .config"],
        ["/home/cryptkeeper/src/ecryptfs",
            "make M=fs/ecryptfs"],
        ["/home/cryptkeeper/src/ecryptfs",
            "cp fs/ecryptfs/ecryptfs.ko ../ecryptfs.ko.%s" % snapshot],
        ]

def install_incremental_kernel_task(snapshot):
    return [
        ["/home/cryptkeeper/src",
            "scp ecryptfs.ko.%s cryptkeeper-test:" % snapshot],
        ["/home/cryptkeeper/src",
            "ssh cryptkeeper-test sudo rmmod ecryptfs"],
        ["/home/cryptkeeper/src",
            "ssh cryptkeeper-test sudo insmod ecryptfs.ko.%s" % snapshot],
        ]

def build_userspace_task(snapshot):
    return [
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "pwd"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git reset --hard origin/master"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git clean -d -x -f"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git checkout upstream"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git pull origin upstream"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git checkout master"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git pull origin master"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git-dch --new-version 104-1cryptkeeper0 --auto --snapshot --snapshot-number %s --git-author" % snapshot],
        ["/home/cryptkeeper/src/ecryptfs_userspace/debian/source",
            "echo 'auto-commit' >> options"],
        ["/home/cryptkeeper/src/ecryptfs_userspace/debian/source",
            "echo 'single-debian-patch' >> options"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "git commit -a -m 'Update debian/changelog (snapshot %s).'" % snapshot],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            'git-buildpackage --git-upstream-tree=branch -b'],
        ]

def install_userspace_task(revision):
    return [
        # TODO(cbhl): Get the SHA and fill in the filename properly.
        ["/home/cryptkeeper/src",
            "scp ecryptfs-utils_104-%(rev)s.?????????_amd64.deb "
            "ecryptfs-utils-dbg_104-%(rev)s.?????????_amd64.deb "
            "libecryptfs0_104-%(rev)s.?????????_amd64.deb "
            "libecryptfs-dev_104-%(rev)s.?????????_amd64.deb "
            "python-ecryptfs_104-%(rev)s.?????????_amd64.deb cryptkeeper-test:"
            % {"rev": revision}],
        ["/home/cryptkeeper/src",
            "ssh cryptkeeper-test sudo dpkg -i "
            "ecryptfs-utils_104-%(rev)s.?????????_amd64.deb "
            "ecryptfs-utils-dbg_104-%(rev)s.?????????_amd64.deb "
            "libecryptfs0_104-%(rev)s.?????????_amd64.deb "
            "libecryptfs-dev_104-%(rev)s.?????????_amd64.deb "
            "python-ecryptfs_104-%(rev)s.?????????_amd64.deb"
            % {"rev": revision}],
        ]

def run_tests_task():
    return [
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "./configure --enable-tests --disable-pywrap"],
        ["/home/cryptkeeper/src/ecryptfs_userspace",
            "make"],
        [None, "ssh cryptkeeper-test mkdir -p src/ecryptfs_userspace"],
        [None, "rsync -arv /home/cryptkeeper/src/ecryptfs_userspace/ "
        "cryptkeeper-test:src/ecryptfs_userspace/"],
        [None, "ssh cryptkeeper-test sudo mkdir /lower"],
        [None, "ssh cryptkeeper-test sudo mkdir /upper"],
        [None, "ssh cryptkeeper-test mkdir /tmp/image"],
        [None, "ssh cryptkeeper-test bash -c 'pwd; cd src/ecryptfs_userspace; "
        "pwd; sudo tests/run_tests.sh -K -c safe -b 1000000 "
        "-D /tmp/image -l /lower -u /upper;'"],
        [None, "ssh cryptkeeper-test bash -c 'pwd; cd src/ecryptfs_userspace; "
        "pwd; sudo tests/run_tests.sh -U -c safe -b 1000000 "
        "-D /tmp/image -l /lower -u /upper;'"],
        [None, "ssh cryptkeeper-test bash -c 'pwd; cd src/ecryptfs_userspace; "
        "pwd; sudo tests/run_tests.sh -K -c destructive -b 1000000 "
        "-D /tmp/image -l /lower -u /upper;'"],
        [None, "ssh cryptkeeper-test bash -c 'pwd; cd src/ecryptfs_userspace; "
        "pwd; sudo tests/run_tests.sh -U -c destructive -b 1000000 "
        "-D /tmp/image -l /lower -u /upper;'"],
    ]

def build(q):
    logging.info("Starting build process...")
    while True:
        logging.info("Waiting for build trigger...")
        build = q.get(True)
        snapshot = get_snapshot()
        revision = get_revision(snapshot)
        tasks = []
        if build["kernel_full"]:
            tasks.append(build_full_kernel_task(revision))
            tasks.append(install_full_kernel_task(revision))
        if build["kernel_incremental"]:
            tasks.append(build_incremental_kernel_task(snapshot))
            tasks.append(install_incremental_kernel_task(snapshot))
        if build["userspace"]:
            tasks.append(build_userspace_task(snapshot))
            tasks.append(install_userspace_task(revision))
        if build["run_tests"]:
            tasks.append(run_tests_task())
        logging.info("BUILD: START")
        for task in tasks:
            logging.info("TASK: START")
            start_time = datetime.datetime.utcnow()
            for command in task:
                if command[0] is None:
                   DEFAULT_DIR = "/home/cryptkeeper/src" #TODO(cbhl): refactor to top
                   logging.info("CWD: %s" % DEFAULT_DIR)
                   os.chdir(DEFAULT_DIR)
                else:
                   logging.info("CWD: %s" % command[0])
                   os.chdir(command[0])
                logging.info("SHELL: %s" % command[1])
                cmd_start_time = datetime.datetime.utcnow()
                popen = subprocess.Popen(command[1],
                                         shell=True, bufsize=4096, stdin=None,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         close_fds=True)
                while True:
                    line = popen.stdout.readline()
                    if not line:
                        cmd_end_time = datetime.datetime.utcnow()
                        cmd_delta = cmd_end_time - cmd_start_time
                        logging.info("SHELL: TIME %s" % cmd_delta)
                        if popen.wait() != 0:
                            logging.info("SHELL: TERMINATED WITH ERRORS")
                        else:
                            logging.info("SHELL: TERMINATED NORMALLY")
                        break;
                    logging.info(line)
            end_time = datetime.datetime.utcnow()
            logging.info("TASK: COMPLETE")
            delta = end_time - start_time
            logging.info("TASK: TIME %s" % delta)
        logging.info("BUILD: COMPLETE")

if __name__ == "__main__":
    logging.basicConfig(
        filename='build.log',
        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: '
        '%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    queue = multiprocessing.Queue(1)
    process = multiprocessing.Process(target=build, args=((queue,)))

    process.start()

    app.run(host='::0',port=20349)

    process.join()
