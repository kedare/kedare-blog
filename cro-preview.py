#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Start hugo with correct parameters from Crostini VM and open the browser on the host (ChromeOS)

import ifaddr
import time
import os
import webbrowser
import threading

def get_lxd_ip():
    eth0 = [adapter.ips for adapter in ifaddr.get_adapters() if adapter.name == "eth0"][0]
    eth0_ipv4 = [ip for ip in eth0 if ip.network_prefix < 32][0]
    return eth0_ipv4.ip

ip = get_lxd_ip()
url = "http://{ip}:1313/".format(ip=ip)
cli = "hugo serve -D -E -F --bind {ip} -b {url}".format(ip=ip, url=url)
os.system(cli)
