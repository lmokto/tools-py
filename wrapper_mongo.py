#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
import unicodedata
import pymongo
import time
from bson.objectid import ObjectId

class Mongo(object):
  #from pudb import set_trace; set_trace()
  
  ExecutionTimeout = pymongo.errors.ExecutionTimeout
  TimeoutError = pymongo.errors.TimeoutError
  OperationFailure = pymongo.errors.OperationFailure
  ConnectionFailure = pymongo.errors.ConnectionFailure
  CollectionInvalid = pymongo.errors.CollectionInvalid
  BulkWriteError = pymongo.errors.BulkWriteError
  CursorNotFound = pymongo.errors.CursorNotFound
  
  def __init__(self, server="localhost", port=27017, db=None, table=None):
    """
      docs
    """
    self.config = {"server": server, "port": port, "db": db, "table": table}
    self.__M = None
    self.new_db = None
    self.new_table = None
    self.__enlc = 0
    self.buildcursor()
    self.buildstatus()
  
  def buildcursor(self):
    """
      docs
    """
    self.cursores = {"CQ": False, "CFI": False, "C":False, "CF": False, "CFO":False}
    self.__CF = None
    self.__CFO = None
    self.__CFI = None
    self.__CQ = None

  def buildstatus(self):
    """
      docs
    """
    self.status = {}
    self.status['connected'] = {"isalive": False, "instance": None}
    self.status['createdError'] = []
    self.status['created'] = []
    self.status['insertedCount'] = []
    self.status['cursor'] = []
    self.status['enlace'] = []
    self.status['backenlace'] = 0
  
  def connection(self):
    """
      docs
    """
    try:
      self.__M = pymongo.Connection(self.config["server"], self.config["port"])
      self.status['connected']['isalive'] = self.__M.alive()
      self.status['connected']['instance'] = self.__M
      return self.status['connected']
    except (self.ConnectionFailure, self.ExecutionTimeout):
      self.status['connected'] = ValueError(" Connection Failure Conectar MongoDB")
      return self.status['connected']
  
  def databases(self):
    """
    docs
    """
    assert hasattr(self.__M, 'database_names')
    return self.__M.database_names()

  def created(self, new_db, new_table):
    """
      docs
    """
    self.new_db = new_db
    self.new_table = new_table
    try:
      self.__M[self.new_db][self.new_table].insert({"nombre": self.new_db})
      self.status['created'].append({'alive':True, 'db':self.new_db, 'table':self.new_table})
      return (self.status["created"]['alive'], self.status["created"]['new_db'], self.status["created"]['new_table'])
    except (self.TimeoutError, self.OperationFailure, self.ConnectionFailure):
      self.status['createdError'].append(ValueError("No se pudo crear {}, {}", (self.new_db, self.new_table)))
      lenerror = len(self.status['createdError'])
      return self.status['createdError'][lenerror-1]
  
  def __enval(self, val):
    """
      docs
    """
    self.status['enlace'].append({"time":time.ctime()[11:19], \
                                  "db": self.config['db'], \
                                  "table": self.config['table']})
    return val
  
  def enlace(self, db, table, new=False):
    """
      docs
    """
    self.__enlc += 1
    if (self.config["db"] and self.config["table"]) == None:
      self.config["db"] = db
      self.config["table"] = table
      return self.__enval(True)
    elif new:
      self.config["db"] = db
      self.config["table"] = table
      return self.__enval(True)
    else:
      return self.__enval(False)
  
  def lastenlace(self):
    """
      docs
    """    
    lenenlace = len(self.status['enlace'])
    return self.status['enlace'][lenenlace-2]
  
  def __inscount(self):
    """
      docs
    """
    self.status['insertedCount'].append({self.config['table']:self.__M[self.config["db"]][self.config["table"]].count()})
    self.lenins = len(self.status['insertedCount'])
    return self.status['insertedCount'][self.lenins-1]

  def collections(self):
    """ docs """
    assert hasattr(self.__M[self.config['db']], 'collection_names')
    return self.__M[self.config['db']].collection_names()

  def insert(self, dictionary):
    """ docs """
    try:
      if self.new_db and self.new_table:
        self.config["db"] = self.new_db
        self.config["table"] = self.new_table
        self.__M[self.config["db"]][self.config["table"]].insert(dictionary)
        return self.__inscount()
      else:
        self.__M[self.config["db"]][self.config["table"]].insert(dictionary)
        return self.__inscount()
    except (self.CollectionInvalid, self.BulkWriteError):
      raise ValueError("CollectionInvalid o Bulk Write Error")
  
  def backenlace(self):
    """ docs """
    if self.__enlc >= 1:
      value = self.lastenlace()
      self.status['backenlace'] += 1
      return self.enlace(value['db'], value['table'], new=True)
    else:
      raise ValueError("conectado en mismo enlace")

  def listenlaces(self):
    return self.status['enlace']

  #import ipdb; ipdb.set_trace();
  def __buildC(self, cursor, func=None):
    """ listquerys, find(), find_one(filter), find_id({'_id':_id}), find(query)"""
    # self.cursores = {"CQ": False, "CFI": False, "C":False, "CF": False, "CFO":False}
    try:
      if cursor == "CQ": 
        self.cursores[cursor] = True
        self.__CQ = self.__M[self.config['db']][self.config['table']].find(func)
        return self.__CQ.clone()
      elif cursor == "CFI": 
        self.cursores[cursor] = True
        self.__CFI = self.__M[self.config['db']][self.config['table']].find_id(func)
        return self.__CFI.clone()
      elif cursor == "CF":
        self.cursores[cursor] = True
        self.__CF = self.__M[self.config['db']][self.config['table']].find()
        return self.__CF.clone()
      elif cursor =="CFO":
        self.cursores[cursor] = True
        self.__CFO = self.__M[self.config['db']][self.config['table']].find_one(func)
        return self.__CFO.clone()
    except self.CursorNotFound:
      self.cursores[cursor] = False
      raise ValueError("of correct type {}".format(self.CursorNotFound))

  def isliveC(self):
    """ docs """
    islives = [(key, value) for key, value in self.cursores.iteritems() if value == True]
    return islives
  
  def querying(self, query={}):
    """ result = mongo.querying({"script" : "string"})"""
    return self.__buildC("CQ", query)

  def findOne(self, filtro):
    """ docs """
    return self.__buildC("CFO", filtro)

  def findID(self, _id):
    """ docs """
    return self.__buildC("CFI", int(_id))

  def find(self):
    """ docs """
    return self.__buildC("CF")

  def info(self):
    """ docs """
    return self.config, self.status, self.cursores

  def exit(self):
    """ docs """
    self.status['connected']['isalive'] = False
    try:
      self.__M.disconnect()
    except:
      raise ValueError("disconnected")

def main():

  mongo_db = Mongo("127.0.0.1", 27017)
  mongo_db.connection()
  mongo_db.enlace("name_db", "name_table")
  mongo_db.insert({"key1": "value1", "key2": "value2", "keyN": "valueN"})
  itercolls = mongo_db.find()
  print next(itercolls)
  print mongo_db.info()

if __name__ == '__main__':
  main()