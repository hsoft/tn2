#/bin/bash

cd /lxdockshare || exit 1
make deb
cp /tmp/tn2.deb build/tn2.deb
chmod o+rw build/tn2.deb
