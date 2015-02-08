#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xively
import datetime
import random
import sched, time

XIVELY_API_KEY = ""
XIVELY_FEED_ID = int()

api = xively.XivelyAPIClient(XIVELY_API_KEY)
feed = api.feeds.get(XIVELY_FEED_ID)
range_pot = [120, 121, 140, 151, 160, 170]
range_time = ["2015-01-24 20:12", "2015-01-24 21:15", "2015-01-24 22:12"]

def run_xively():
	now = datetime.datetime.utcnow()
	# asegurar que sea de tipo int
	potencia = random.randrange(0, 101, 2)
	watts = random.randrange(5, 80, 2)
	print "post is being done"
	print "at :", now
	print "potencia :", potencia
	print "watts :", watts
	if now == range_time[0]:
		feed.datastreams = [
			xively.Datastream(id='potencia', current_value=range_pot[0], at=now),
			xively.Datastream(id='watts', current_value=watts, at=now),
		]
	elif now == range_time[1]:
		feed.datastreams = [
			xively.Datastream(id='potencia', current_value=range_pot[1], at=now),
			xively.Datastream(id='watts', current_value=watts, at=now),
		]
	elif now == range_time[2]:
		feed.datastreams = [
			xively.Datastream(id='potencia', current_value=range_pot[2], at=now),
			xively.Datastream(id='watts', current_value=watts, at=now),
		]
	feed.update()
	s.enter(5, 1, run_xively, ())

s = sched.scheduler(time.time, time.sleep)
s.enter(5, 1, run_xively, ())
s.run()