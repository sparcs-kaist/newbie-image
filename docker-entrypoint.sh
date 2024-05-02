#!/bin/sh

echo "sparcs:$NEW_PASSWORD" | chpasswd
if [ ! -f /home/sparcs/.profile ]; then
    tar -xzf /sparcs-home.tar.gz -C /
fi
mkdir -p /var/run/sshd
/usr/sbin/sshd -D
tail -f /dev/null
