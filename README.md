# Installation

1. sudo aptitude install virtualenv ccache less \
kernel-package build-essential bc \
debhelper dh-autoreconf git-buildpackage \
intltool libgcrypt11-dev libglib2.0-dev libkeyutils-dev libnss3-dev \
libpam0g-dev pkg-config python-dev swig
2. virtualenv --distribute ~/.virtualenv/fydp\_build/
3. source ~/.virtualenv/fydp\_build/bin/activate
4. pip install -r requirements.txt
5. git clone --depth 1 git://github.com/zmanji/ecryptfs.git
6. git clone --depth 1 git://github.com/zmanji/ecryptfs\_userspace.git
7. export PATH="/usr/lib/ccache:$PATH"
8. python build.py
