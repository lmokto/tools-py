#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
import pymongo

filename = ''

class Mongo(object):
  def __init__(self, server, port, db=None, table=None):
    self.m_date = {"server": server, "port": port, "db": db, "table": table}
  def connection(self):
    self.mongo = pymongo.Connection(self.m_date["server"], self.m_date["port"])
  def created(self, dbNew, tableNew):
    self.dbNew = dbNew
    self.tableNew = tableNew
    self.mongo[self.dbNew][self.tableNew].insert({"nombre": self.dbNew})
  def insert(self, dictionary):
    if self.dbNew and self.tableNew:
      self.m_date["db"] = self.dbNew
      self.m_date["table"] = self.tableNew
      self.mongo[self.m_date["db"]][self.m_date["table"]].insert(dictionary)
    else:
      assert self.m_date["db"] and self.m_date["table"]
      self.mongo[self.m_date["db"]][self.m_date["table"]].insert(dictionary)

mongo_db = Mongo("localhost", 27017)
mongo_db.connection()
mongo_db.created("", "")

Models = {
  "script": "string",
  "description": "string",
  "arguments" : ["string"],
  "usage": ["string"],
  "category": ["string"],
  "script_id": "ObjectId"
}

with open(filename, 'rb') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
          mongo_db.insert({
      			'script': row[0],
      			'usage' : row[1],
            'description' :row[2]
          })
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))