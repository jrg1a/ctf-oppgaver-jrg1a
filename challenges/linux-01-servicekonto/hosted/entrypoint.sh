#!/bin/sh
set -eu

mkdir -p /var/run/sshd

exec /usr/sbin/sshd -D
