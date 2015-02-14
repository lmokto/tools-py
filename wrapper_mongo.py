#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
import pymongo
import time
import types
from bson.objectid import ObjectId

class Mongo(object):

  ExecutionTimeout = pymongo.errors.ExecutionTimeout
  TimeoutError = pymongo.errors.TimeoutError
  OperationFailure = pymongo.errors.OperationFailure
  ConnectionFailure = pymongo.errors.ConnectionFailure
  CollectionInvalid = pymongo.errors.CollectionInvalid
  BulkWriteError = pymongo.errors.BulkWriteError
  CursorNotFound = pymongo.errors.CursorNotFound
  
  def __init__(self, server, port, db=None, table=None):
    """
      docs
    """
    self.__M = None
    self.buildcursor()
    self.buildstatus()
    self.new_db = None
    self.new_table = None
    self.config = {"server": server, "port": port, "db": db, "table": table}
  
  def buildcursor(self):
    """
      docs
    """
    self.cursores = {"CQ": False, "CFI": False, "C":False, "CF": False, "CFO":False}
    self.__C = None
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
    assert self.status['connected'].get('isalive')
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
    self.status['enlace'].append({time.ctime()[11:19], self.config['db'], self.config['table']})
    return val
  
  def enlace(self, db, table, new=False):
    """
      docs
    """
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
      print ValueError("CollectionInvalid o Bulk Write Error")
  
  def bulkinsert(self):
    pass
  
  def backenlace(self):
    """ docs """
    value = list(self.lastenlace())
    self.status['backenlace'] += 1
    return self.enlace(value[1], value[2], new=True)

  def __buildC(self, cursor, func):
    """ listquerys, find(), find_one(filter), find_id({'_id':_id}), find(query)"""
    try:
      self.cursores[cursor] = True
      builc = "self.__M[self.config['db']][self.config['table']].{0}".format(func)
      
    except self.CursorNotFound:
      self.cursores[cursor] = False
      raise ValueError("of correct type {}".format(self.CursorNotFound))

  def isliveC(self):
    """ docs """
    islives = [(key, value) for key, value in self.cursores.iteritems() if value == True]
    return islives
  
  def clone(self, cursor):
    """ docs """
    namec = cursor
    islive = self.cursores.get(cursor)
    if islive:
      return eval("self.__{0}".format(namec)).clone()
    else:
      return self.isliveC()

  def querying(self, query={}):
    """ result = mongo.querying({"script" : "string"})"""
    return self.__buildC("CQ", "find_one({0})".format(filtro))

  def findOne(self, filtro):
    """ docs """
    return self.__buildC("CFO", "find_one({0})".format(filtro))

  def findID(self, _id=int):
    """ docs """
    return self.__buildC("CFI", "find_id({'_id':{0}})".format(_id))

  def find(self):
    """ docs """
    return self.__buildC("CF", "find()")

  def info(self):
    """ docs """    
    return self.config, self.status, self.cursores