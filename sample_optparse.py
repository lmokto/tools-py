#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
parser = optparse.OptionParser('usage %prog -H <target host> -p <target port>')
parser.add_option('-H', dest='tgHost', type='string', help='specify target host')
parser.add_option('-p', dest='tgPort', type='int', help='specify target host')
(options, args) = parser.parse_args()
tgtHost = options.tgtHost
tgtPort = oprtions.tgtPort
if(tgtHost == None) | (tgtPort == None):
	print parser.usage
	exit(0)

