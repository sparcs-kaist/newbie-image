#!/bin/sh

echo "sparcs:$NEW_PASSWORD" | chpasswd
if [ -f /home/sparcs/.profile ]; then
    tar xvf /sparcs-home.tar.gz -C /home/sparcs
fi
mkdir -p /var/run/sshd
/usr/sbin/sshd -D
tail -f /dev/null
