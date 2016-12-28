#!/usr/bin/python

import argparse
import time

from tabulate import tabulate

PROC_FS_S_IRQS = "/proc/softirqs"
PROC_FS_H_IRQS = "/proc/interrupts"

class Irq:
    def __init__(self, name, data):
        self.occurrences = data 
        self.name = name

    def total(self):
        return sum(self.occurrences)

    def cpu_share_percent(self):
        total = self.total()
        if total != 0:
            return [ float( (irq_n * 100 ) / total ) for irq_n  in self.occurrences ]
        else:
            return self.occurrences[:]

    def get_occ(self):
        return self.occurrences[:]

    def __getitem__(self, i):
        return self.occurrences[i]

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
            if len (raw_l_refined[1:len(col_head)+1]) < len(col_head):
                    continue
            name = "%s %s" % ("".join(raw_l_refined[len(col_head)+1:]), name)
        _Irqs.append(Irq(name, [ int(i) for i in raw_l_refined[1:len(col_head)+1] ]))
    return col_head, _Irqs

def merge_rate_meas(abstr_l, delta):
    merged_Irq_abstr = []
    diff = lambda x: float((x[0] - x[1]) / delta)
    for elem1, elem2 in map(None, abstr_l[0], abstr_l[1]):
        elem2.occurrences = map(diff, zip(elem2.get_occ(), elem1.get_occ()))
        merged_Irq_abstr.append( elem2 )

    return merged_Irq_abstr 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Frontend to irqs (soft | hard) proc fs')
    parser.add_argument("-p", '--perc', default=False, help='show CPU taken by IRQ in percentage', action='store_true')
    parser.add_argument("-t", dest="total", default=False, help='total up irqs per channel', action='store_true')
    parser.add_argument("-s", dest="sort", help='CPU num to sort by') 
    parser.add_argument("-r", "--rate", dest="rate", help='determine rate per sec for interval', nargs=2)
    parser.add_argument("--hard", dest="hard", help='showing hardirqs', default=False, action='store_true')

    args = parser.parse_args()

    raw = []
    _Irqs = []
    col_head = []
    if not args.rate:
        raw = procfs_read_raw(PROC_FS_H_IRQS if args.hard else PROC_FS_S_IRQS)
        col_head, _Irqs = form_irq_abstraction(raw, args)
    else:
        delta = int(args.rate[1]) - int(args.rate[0])
        raw_l = []
        raw_l.append(procfs_read_raw(PROC_FS_H_IRQS if args.hard else PROC_FS_S_IRQS))
        time.sleep( delta )
        raw_l.append(procfs_read_raw(PROC_FS_H_IRQS if args.hard else PROC_FS_S_IRQS))
        abstr_l = []
        for raw in raw_l:
            col_head, _Irq_abstr = form_irq_abstraction(raw, args)
            abstr_l.append(_Irq_abstr)
        _Irqs = merge_rate_meas(abstr_l, delta)

    if args.total:
        col_head.append("total") 

    if args.sort:
        index = int(args.sort)
        key_f = lambda x: x[index]
        cmp_f = lambda x,y: y - x
        _Irqs = sorted(_Irqs, cmp=cmp_f, key=key_f)

    table = []
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
 
