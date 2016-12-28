# opes

Place for tools/utilities

# irq_reeler.py

```
usage: irq_reeler.py [-h] [-p] [-t] [-s SORT] [-r RATE RATE] [--hard]

Frontend to irqs (soft/hard) proc fs

optional arguments:
  -h, --help            show this help message and exit
  -p, --perc            show CPU taken by softIRQ in percentage
  -t                    total up softirqs per channel
  -s SORT               CPU num to sort by
  -r RATE RATE, --rate RATE RATE
                        determine rate per sec for interval
  --hard                showing hardirqs

Does what says on tin:

E.g:

python irq_reeler.py --rate 1 5 -t
                 CPU0    CPU1    CPU2    CPU3    CPU4    CPU5    CPU6    CPU7    total
HI:                 0       0       0       0       0       0       0       0        0
TIMER:            108     196     126      54      38      23      37       3      585
NET_TX:             0       0       0       0       0       0       0       0        0
NET_RX:            10       6       8       2      87       0       0       0      113
BLOCK:             12       0       0       0       0       0       0       0       12
BLOCK_IOPOLL:       0       0       0       0       0       0       0       0        0
TASKLET:            1       0       0       0       0       0       0       0        1
SCHED:            105     191     117      54      36      23      33       3      562
HRTIMER:            0       0       0       0       0       0       0       0        0
RCU:               85     161      92      43      31      26      22       3      463

Gives you the rate per sec softirqs are processed at certain CPUS.
```
