#!/bin/bash

HOST="tn2@next.threadandneedles.org"
DEST="/opt/tn2"

rsync Makefile requirements.freeze "$HOST:$DEST"
rsync -r --delete install src "$HOST:$DEST"
ssh "$HOST" "${DEST}/postdeploy.sh"
