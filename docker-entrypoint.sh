#!/bin/sh

echo "sparcs:$NEW_PASSWORD" | chpasswd
mkdir -p /var/run/sshd
/usr/sbin/sshd -D
tail -f /dev/null
