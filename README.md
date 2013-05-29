# Installation on the test server

1. sudo aptitude install debhelper autotools-dev autoconf automake \
intltool libtool libgcrypt11-dev libglib2.0-dev libkeyutils-dev \
libnss3-dev libpam0g-dev pkg-config python-dev swig acl ecryptfs-utils \
libgpgme11-dev libopencryptoki-dev libpkcs11-helper1-dev libtspi-dev

# Installation on the build server

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
8. ssh-keygen; ssh-copy-id cryptkeeper-test; ssh -N -o StrictHostKeyChecking=no cryptkeeper-test
9. python build.py

# Random Notes

1. Buildbot needs a reasonable amount of RAM (try 512 MB).
2. ccache hits the disk a lot, use VirtIO instead of IDE emulation.
3. echo 'sys.kernel.printk = 7 4 1 7' >> /etc/sysctl.conf && sudo sysctl -p

