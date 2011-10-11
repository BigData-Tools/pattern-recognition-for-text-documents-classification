# -*- coding: utf-8 -*-
import operator
import numpy

from pymongo import Connection

from bag import bag_of_words

db = Connection().theses
db.features.ensure_index('field')

account = {}
freqs = {}

for t in db.theses.find():
    if 'data' in t and len(t['data']) > 10:
        if t['field'] not in account:
            account[t['field']] = 0
        account[t['field']] += 1
print 'total:',account

for field in account:
    print 'Creating frequency map for', field
    f = {}
    for t in db.theses.find({'field': field}):
        # Wrong data
        if 'data' not in t:
            continue

        bag = bag_of_words(t['data'])
        for item in bag:
            if item not in f:
                f[item] = 1
            else:
                f[item] += 1
    freqs[field] = f

print 'Found frequencies, now filtering...'

for name, field in freqs.items():
    fcut = (0.3*numpy.max(field.values()) + 0.7*numpy.mean(field.values()))/2.0
    freqs[name] = dict((k, v) for k, v in field.iteritems() if v > fcut)

    max = numpy.max(freqs[name].values())
    min = numpy.min(freqs[name].values())
    print '\n%s (cut=%d, min=%d, max=%d)' % (name, fcut, min, max)
    print '\tfeature dimension=%d' % len(freqs[name])
    print '\tMost frequent:', freqs[name].keys()[0:10]

    db.features.update({"field": name}, {"field": name, "features": freqs[name]}, upsert=True)