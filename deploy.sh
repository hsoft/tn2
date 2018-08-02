#!/bin/bash

HOST="tn2@www.threadandneedles.org"
DEST="/opt/tn2"

rsync Makefile "$HOST:$DEST"
rsync -r --delete install src "$HOST:$DEST"
ssh "$HOST" "${DEST}/postdeploy.sh"
