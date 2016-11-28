#!/usr/bin/env python

ips = [u'10.0.42.201', u'10.0.42.234', u'10.0.42.42', u'10.0.42.10', u'10.0.42.150', u'10.0.42.1', u'10.0.42.220', u'10.0.42.6']
print "Before sorting"
for x in ips:
    print x

for i in range(len(ips)):
    ips[i] = tuple((int(x) for x in ips[i].split(".")))

ips.sort()

for i in range(len(ips)):
    ips[i] = ".".join((str(x) for x in ips[i]))


print "After sorting"
for x in ips:
    print x
