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
2. sudo aptitude install python-software-properties # to add redis PPA
3. sudo add-apt-repository ppa:rwky/redis # for redis-server
4. sudo aptitude install redis-server
5. virtualenv --distribute ~/.virtualenv/fydp\_build/
6. source ~/.virtualenv/fydp\_build/bin/activate
7. pip install -r requirements.txt
8. git clone --depth 1 git://github.com/zmanji/ecryptfs.git
9. git clone --depth 1 git://github.com/zmanji/ecryptfs\_userspace.git
10. export PATH="/usr/lib/ccache:$PATH"
11. ssh-keygen; ssh-copy-id cryptkeeper-test; ssh -N -o StrictHostKeyChecking=no cryptkeeper-test
12. git config --global user.name "Team CryptKeeper Build Bot"
13. git config --global user.email "cryptkeeper@cryptkeeper-build.kvm.myazuresky.com"
14. gpg --gen-key
15. python build.py

# Random Notes

1. Buildbot needs a reasonable amount of RAM (try 512 MB).
2. ccache hits the disk a lot, use VirtIO instead of IDE emulation.
3. echo 'sys.kernel.printk = 7 4 1 7' >> /etc/sysctl.conf && sudo sysctl -p

