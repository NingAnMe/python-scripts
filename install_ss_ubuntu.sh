#!/usr/bin/env bash

# Ubuntu 14.04 16.04

server="123.123.123.123"  # your vps ip
post=443  # post
password="password"  # password


echo "==================================="
echo "Start install SS"

# add repository
apt-get install software-properties-common
add-apt-repository ppa:max-c-lv/shadowsocks-libev

# upgrade
apt-get update

# install ss
apt install shadowsocks-libev

# install rng tool
apt-get rng-tools
rngd -r /dev/urandom

# make config
config_dir="/etc/shadowsocks-libev/"
config_file="/etc/shadowsocks-libev/config.json"

if [ ! -d ${config_dir} ]; then
    mkdir /etc/shadowsocks-libev
fi

if [ ! -f ${config_file} ]; then
    touch /etc/shadowsocks-libev/config.json
fi

config="{
\"server\":\"${server}\",
\"server_port\":${post},
\"password\":\"${password}\",
\"timeout\":999,
\"method\":\"aes-256-cfb\"
}"

echo "${config}" > ${config_file}

echo "Install SS done"
echo "==================================="
