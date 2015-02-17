#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wraper_mongo import Mongo
import redis

class itercolls(Mongo):

  def __init__(self, host="localhost", port=6379, db=0):

    Mongo.__init__(self, server="localhost", port=27017, db=None, table=None)
    self.unix_socket_path = None
    self.configCli = {"host" : host, "port":port, "db": db}
    self.connected()

  def connected(self):
    self.client = redis.StrictRedis(host=self.configCli["host"], port=self.configCli["port"], db=self.configCli["db"])

  def instance(self, mongo_config={}, schema={}):
    self.__itc = 0
    self.__sch = schema
    self.config['server'] = mongo_config["host"]
    self.config['port'] = mongo_config["port"]
    self.connection()
    self.enlace(mongo_config["db"], mongo_config["table"])

  def set(self, key, insert):
    if not self.client.exists(key):
      self.client.set(key, insert)

  def get(self, key):
    iternext = self.client.get(key)
    if not iternext:
      iternext = self.findOne({"_id": key})
      assert iternext
      _id = iternext["_id"]
      iternext.pop(_id)
      self.set(_id, iternext)
      return iternext
    else:
      return iternext

  def validate(self, ckeys):
    skeys = self.__sch.keys()
    skeys.sort()
    ckeys.sort()
    if ckeys == skeys:
      return True
    else:
      return False

  def next(self):
    count = 0
    if self.cursores["CF"] == False:
      self.__iter = self.find()
      count = self.__iter.count()
    elif self.__itc == count:
      raise ValueError("limit")
    self.__itc += 1
    iternext = self.__iter.next()
    result = self.validate(iternext.keys())
    if result:
      _id = iternext["_id"]
      iternext.pop(_id)
      self.set(iternext["_id"], iternext)
    return iternext


def main():
  
  schema = {"_id": str, "key1": str, "key2": str, "key3": str}
  config = {"host":"localhost", "port":27017, "db":"my_db", "table":"my_table"}
  insmon = itercolls()
  insmon.instance(config, schema)
  
  print insmon.next()
  print insmon.next()
  print insmon.next()
  print insmon.next()