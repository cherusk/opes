#!/usr/bin/python

#Copyright (C) 2016  Matthias Tafelmeier

#lindwurm is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#lindwurm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import subprocess




CONF_ROOT = "/sys/class/net/"

def determine_tx_qu_num():
    cmd='ls -d /sys/class/net/%s/queues/tx-* | wc -l' % (iface)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    (out, err) = p.communicate()
    
    return int(out)

#bitmask transl.
def form_per_cpu_bitmask(cpu):
    return 1 << cpu

def set_cpu_xps_mask(cpu, qu, preserve=False):
    xps_f_path = os.path.join(CONF_ROOT, iface, "queues", "tx-" + str(qu), "xps_cpus") 
    with open(xps_f_path, "rw+") as xps_f:
        bitmask = form_per_cpu_bitmask(cpu)
        if preserve:
            previos = xps_f.read()
            previos = previos.replace(",", "").strip()
            previos = int(previos, base=16)
            bitmask = bitmask | previos
        out = "%x" % bitmask
        xps_f.write(out) 

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description='cpu to tx driver queues distribution mechanism')

    ap.add_argument('-c', '--cpu_num', help='effective cpu number of node')
    ap.add_argument('-i', '--iface', help='interface which holds the tx queues')

    args = ap.parse_args()
    
    cpu_num= int(args.cpu_num)
    iface= args.iface

    tx_qu_num = determine_tx_qu_num()

    non_shared_ratio = tx_qu_num / cpu_num
    tx_shared_qus_num = tx_qu_num - (cpu_num * non_shared_ratio)
    tx_non_shared_qus_num = tx_qu_num - tx_shared_qus_num

    for qu in range(0, tx_non_shared_qus_num):
        mod_qu = qu % (cpu_num)
        set_cpu_xps_mask(mod_qu, qu)

    for qu in range(tx_non_shared_qus_num, tx_qu_num):
        for cpu in range(0, cpu_num):
            set_cpu_xps_mask(cpu, qu, preserve=True)
