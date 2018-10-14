#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/7/20 11:05
@Author  : AnNing
"""
import os
import sys
import getopt


def main():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "hvj:s:t:", ["version", "help", "job=", "sat=" "time="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(1)
    print opts
    print _
    for k, v in opts:
        print k, v


if __name__ == '__main__':
    main()
