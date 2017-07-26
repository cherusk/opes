#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Matthias Tafelmeier

# tcp_pcap_retrans.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# tcp_pcap_retrans.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from scapy.all import *
import argparse
from collections import OrderedDict
from collections import Callable

_TCP = 6

def form_fl_key(tcp_h, ip_h):
    return "%s#%-10s%s#%s" % (ip_h.src,
                              tcp_h.sport,
                              ip_h.dst,
                              tcp_h.dport)

def form_peer_key(tcp_h, ip_h):
    return "%-20s%s" % (ip_h.src, ip_h.dst)

def depict_fl(stats):
    #as OrderedDict key arg was failing
    out_l = sorted([(k, v['cnt']) for k, v in stats.items()], key=lambda f:f[1])
    print "%s | %s" % ("flow", "retrans_cnt")
    for f in out_l:
        print "%s | %s" % (f[0], f[1])

def depict_peer(stats):
    data = [(k, sum([f['cnt'] for f in v.values()])) for k, v in stats.items()]
    out_l = sorted(data, key=lambda f:f[1])
    print "%s | %s" % ("peer", "retrans_cnt")
    for f in out_l:
        print "%s | %s" % (f[0], f[1])

class Logic(Callable):

    stats = {}

    def __init__(self, args):
        if args.by_peer:
            self.c_depict = depict_peer
            self.c_form_key = form_peer_key
            self.c_cnt = self.cnt_peer
        else:
            self.c_depict = depict_fl
            self.c_form_key = form_fl_key
            self.c_cnt = self.cnt_fl

    def cnt_peer(self, k, tcp_h, ip_h):
        port_k = "%s%s" % (tcp_h.sport, tcp_h.dport)
        if k not in self.stats.keys():
            self.stats[k] = { port_k: { 'seq' : tcp_h.seq, 'cnt': 0 }}
        else:
            if port_k not in self.stats[k].keys():
                self.stats[k][port_k] = { 'seq' : tcp_h.seq, 'cnt': 0 }
            elif (self.stats[k][port_k]['seq'] >= tcp_h.seq):
                print self.stats[k][port_k]
                self.stats[k][port_k]['cnt'] = self.stats[k][port_k]['cnt'] + 1

    def cnt_fl(self, k, tcp_h, ip_h):
        if k not in self.stats.keys():
            self.stats[k] = { 'seq' : tcp_h.seq, 'cnt': 0 }
        else:
            if (self.stats[k]['seq'] >= tcp_h.seq):
                self.stats[k]['cnt'] = self.stats[k]['cnt'] + 1

    def __call__(self, pkts):
        for p in pkts:
            ip_h = p[IP]
            if ip_h.proto == _TCP:
                tcp_h = p[TCP]
                k = self.c_form_key(tcp_h, ip_h)
                self.c_cnt(k, tcp_h, ip_h)
        self.c_depict(self.stats)

def run():
    parser = argparse.ArgumentParser(description='Utility to legacy way ascertain highest retransmitters')
    parser.add_argument('-i', '--in_file', help="input pcap", required=True)
    parser.add_argument('-d', '--by_peer', help="set granularity level to peer node", action='store_true')
    args = parser.parse_args()

    pkts = rdpcap(args.in_file)

    Logic(args)(pkts)

if __name__ == "__main__":
    run()
