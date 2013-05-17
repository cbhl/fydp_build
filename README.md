# Installation

1. sudo aptitude install kernel-package build-essential virtualenv ccache bc debhelper less
2. virtualenv --distribute ~/.virtualenv/fydp\_build/
3. source ~/.virtualenv/fydp\_build/bin/activate
4. pip install -r requirements.txt
5. git clone --depth 1 git://github.com/zmanji/ecryptfs.git
6. git clone --depth 1 git://github.com/zmanji/ecryptfs\_userspace.git
7. export PATH="/usr/lib/ccache:$PATH"
8. python build.py
