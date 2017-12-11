#/bin/bash

cd /vagrant || exit 1
rm -rf /tmp/tn2*
make deb
cp /tmp/tn2.deb build/tn2.deb
chmod o+rw build/tn2.deb

# every time we build a .deb, we want to update requirements.freeze
# requirements.freeze isn't actually used, but it's there for informational purposes,
# to track dependency changes in the python venv.
./scripts/freezedeps.sh
