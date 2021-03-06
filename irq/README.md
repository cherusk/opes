# install

\# pip install irq_reeler

# irq_reeler

A tool meant to make linux interrupts userland analysis more convenient.

```
usage: irq_reeler [-h] [-p] [-t] [-s SORT] [-r SECS] [--hard]
                  [--range CPUX-CPUY,CPUZ] [-c INTERVAL REPETITIONS]

Frontend to the linux kernel exported IRQs (soft and hard) procfs interface

optional arguments:
  -h, --help            show this help message and exit
  -p, --perc            show CPU taken by IRQ channel in percentage
  -t                    total up IRQs per channel
  -s SORT               CPU num to sort by
  -r SECS, --rate SECS  determine rate of occurrences per sec for interval
  --hard                showing hardIRQs
  --range CPUX-CPUY,CPUZ
                        cpu range to focus
  -c INTERVAL REPETITIONS
                        repeat times the interval in secs



Does what says on the tin:

E.g.:

$ irq_reeler --rate 5 -t --range 0-7
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
