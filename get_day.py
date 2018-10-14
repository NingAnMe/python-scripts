#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/7/12 14:35
@Author  : AnNing
"""

from PB.pb_time import time_block


def get_day_new(l, activity):
    days = {}

    for x in l:
        day_x, activity_x = x

        day = days.get(day_x, {})

        day['time'] = day.get('time', 0) + 1

        if activity_x != activity:
            days[day_x] = day
            continue

        day[activity_x] = day.get(activity_x, 0) + 1

        days[day_x] = day
    l = sorted(days, key=lambda x: (days[x].get('time', 0), days[x].get(activity, 0)))
    return l[0]


def get_day(l, activity):
    d = {}

    for x in l:
        if x[0] not in d.keys():
            d[x[0]] = []
        d[x[0]].append(x[1])

    d = {k: [v.count(activity), len(v)] for k, v in d.items()}

    l = [[k, v[0], v[1]] for k, v in d.items()]

    l = sorted(l, key=lambda x: (x[1], x[2]))
    return l[0][0]


if __name__ == '__main__':
    mylist = [['Day 1', 'Activity A'], ['Day 2', 'Activity A'], ['Day 1', 'Activity A'], ['Day 2', 'Activity C'],
              ['Day 2', 'Activity D']]
    mylist = mylist * 50
    for i in xrange(10):
        with time_block('new'):
            for i in xrange(100000):
                get_day_new(mylist, 'Activity D')

        with time_block('old'):
            for i in xrange(100000):
                get_day(mylist, 'Activity D')
