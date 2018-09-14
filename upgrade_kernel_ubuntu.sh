#!/usr/bin/env bash

# Ubuntu 14.04 16.04

echo "==================================="
echo "Start upgrade Ubuntu Kernel 4.18.7"

if [! -f "linux-image-4.16.0-041600-generic_4.16.0-041600.201804012230_amd64.deb"]; then
    wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.16/linux-image-4.16.0-041600-generic_4.16.0-041600.201804012230_amd64.deb
fi

dpkg -i linux-image-4.*.deb

update-grub

echo "Upgrade kernel done"
echo "==================================="
