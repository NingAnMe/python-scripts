#!/usr/bin/env bash

# Ubuntu 14.04 16.04

echo "==================================="
echo "Start open BBR"

# open
modprobe tcp_bbr

echo "tcp_bbr" >> /etc/modules-load.d/modules.conf

echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf

echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf

sysctl -p

# check
sysctl net.ipv4.tcp_available_congestion_control

sysctl net.ipv4.tcp_congestion_control

echo "Open BBR done"
echo "==================================="
