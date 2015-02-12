#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
import httplib
import csv

host = ''
path = ''
label = ''

def extract(host, path, label):
	conn = httplib.HTTPConnection(host)
	conn.putrequest("GET", path)
	header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36", "Cache-Control": "no-cache", }
	conn.endheaders()
	res = conn.getresponse()
	if (res.status == 200):
		source = res.read()
		len(source)
		dochtml = html.fromstring(source)
		conn.close()
		return dochtml.cssselect(label)[0].text
	else:
		conn.close()
		print res.status
		raise("host fallo")


result = extract(host, path, label)
print result