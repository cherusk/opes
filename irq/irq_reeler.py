#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Matthias Tafelmeier

# irq_reeler.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# irq_reeler.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import argparse
import time
from time import sleep

from tabulate import tabulate

PROC_FS_S_IRQS = "/proc/softirqs"
PROC_FS_H_IRQS = "/proc/interrupts"


class Irq:
    def __init__(self, name, data, _range):
        if _range:
            self.occurrences = Irq.filter_range(data, _range)
        else:
            self.occurrences = data
        self.name = name

    def total(self):
        return sum(self.occurrences)

    def cpu_share_percent(self):
        total = self.total()
        if total != 0:
            return [float((irq_n * 100) / total) for irq_n in self.occurrences]
        else:
            return self.occurrences[:]

    def get_occ(self):
        return self.occurrences[:]

    def __getitem__(self, i):
        return self.occurrences[i]

    @classmethod
    def filter_range(cls, data, _range):
        out = []
        for subr in _range:
            if isinstance(subr, list):
                out.extend(data[subr[0]:subr[1]])
            elif isinstance(subr, int):
                out.append(data[subr])
            else:
                raise RuntimeError("unexpected subrange")

        return out


def procfs_read_raw(_file):
    raw = ""
    with open(_file, "r") as irqs_f:
        raw = irqs_f.read()

    return raw


def form_irq_abstraction(raw, args):
    _Irqs = []
    raw_list = raw.splitlines()
    col_head = raw_list[0].split()
    for raw_l in raw_list[1:]:
        raw_l_refined = raw_l.split()
        name = raw_l_refined[0]
        if args.hard:
            if len(raw_l_refined[1:len(col_head)+1]) < len(col_head):
                    continue
            name = "%s %s" % ("".join(raw_l_refined[len(col_head)+1:]), name)
        _Irqs.append(Irq(name,
                     [int(i) for i in raw_l_refined[1:len(col_head)+1]],
                     args._range))
    return col_head, _Irqs


def merge_rate_meas(abstr_l, delta):
    merged_Irq_abstr = []
    diff = lambda x: float((x[0] - x[1]) / delta)
    for elem1, elem2 in map(None, abstr_l[0], abstr_l[1]):
        elem2.occurrences = map(diff, zip(elem2.get_occ(), elem1.get_occ()))
        merged_Irq_abstr.append(elem2)

    return merged_Irq_abstr


def determ_focus(args):
    return PROC_FS_H_IRQS if args.hard else PROC_FS_S_IRQS


def do_outp(col_head, _Irqs, args):
    table = []

    if args.sort:
        index = int(args.sort)
        key_f = lambda x: x[index]
        cmp_f = lambda x, y: y - x
        _Irqs = sorted(_Irqs, cmp=cmp_f, key=key_f)

    if args._range:
        col_head = Irq.filter_range(col_head, args._range) 

    if args.total:
        col_head.append("total")

    for irq in _Irqs:
        if args.perc:
            outl = irq.cpu_share_percent()
        else:
            outl = irq.get_occ()
        if args.total:
            outl.append(irq.total())
        outl.insert(0, irq.name)
        table.append(outl)

    print tabulate(table, headers=col_head, tablefmt="plain")

def parse_range(args):
    args._range = args._range.strip().split(",")
    singl_cpus = [int(x) for x in args._range if x.find("-") == -1]
    subranges = [x for x in args._range if x.find("-") > 0]
    subranges = [x.split("-") for x in subranges]
    subranges = [[int(x[0]), int(x[1]) + 1] for x in subranges]
    args._range = []
    args._range.extend(singl_cpus)
    args._range.extend(subranges)
    print args._range

def run(args):
    raw = []
    Irqs = []
    col_head = []
    focus = determ_focus(args)

    if args._range:
        parse_range(args)

    if args.rate:
        delta = int(args.rate)
        raw_l = []
        raw_l.append(procfs_read_raw(focus))
        time.sleep(delta)
        raw_l.append(procfs_read_raw(focus))
        abstr_l = []
        for raw in raw_l:
            col_head, _Irq_abstr = form_irq_abstraction(raw, args)
            abstr_l.append(_Irq_abstr)
        _Irqs = merge_rate_meas(abstr_l, delta)
    else:
        raw = procfs_read_raw(focus)
        col_head, _Irqs = form_irq_abstraction(raw, args)

    do_outp(col_head, _Irqs, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Frontend to irqs (soft | hard) proc fs')
    parser.add_argument("-p", '--perc', default=False, help='show CPU taken by IRQ in percentage', action='store_true')
    parser.add_argument("-t", dest="total", default=False, help='total up irqs per channel', action='store_true')
    parser.add_argument("-s", dest="sort", help='CPU num to sort by')
    parser.add_argument("-r", "--rate", dest="rate", help='determine rate per sec for interval', metavar="SECS")
    parser.add_argument("--hard", dest="hard", help='showing hardirqs', default=False, action='store_true')
    parser.add_argument("--range", dest="_range", help='cpu range to focus', default=None, metavar="CPUX-CPUY,CPUZ")
    parser.add_argument("-c", dest="continuous", help='repeat times the interval in secs',
                        type=int, default=(0, 1), metavar=('INTERVAL', 'REPETITIONS'), nargs=2)

    args = parser.parse_args()

    dec = lambda x : x - 1

    repeat = args.continuous[1]
    interval = float(args.continuous[0])

    while repeat:
        run(args)
        sleep(interval)
        repeat = dec(repeat)
