#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from redis import StrictRedis
from hashlib import sha1

"""

clase que hereda las operaciones de redis y mongo

operamos sobre CRUD

###
crear 

redis

ID con diferentes flags

id : hash?? o que???

created: CRD ( entero varor 0 o 1)
intentos creacion: TRY ( counter, entero valor +1 )

readed: RDE
count readed : CRDE

updated : UPD
count update : CUPD

deleted : DLT

antes de crear un elemento, averiguamos que tipo de flag tiene,

yo cuando recibo el elemento a crear no conozco su identificador por mas que ya este creado
primero tengo que consultar en cache si ya esta creado, antes de ir hacer una operacion en disco


por ejemplo, voy a crear un elemento, que dispone de tres llave con sus valores,
creamos el hash del elemento, que es el identificador en redis, verificamos si existe en redis
en caso de estar, nos fijamos que tipo de flags dispone,

CREATED
	IF NO CREADO
		GUARDAMOS
			ASIGNAMOS FLAGS | CRD = 1, RDE = 0, UPD = 0, DLT = 0 TRY = 0
	IF CREADO PERO ESTA SIN ELIMINAR (CRD = 1 and DLT = 0)
		NO GUARDAMOS
			asignamos un intento de creacion al elemento
			TRY += 1
			CONTINUE
	IF CREADO PERO FUE ELIMINADO (CRD = 1 AND DLT = 1)
		NO GUARDAMOS
			asignamos un intento de creacion al elemento
			TRY += 1
			CONTINUE


antes de realizar la consulta en una db, primero averiguamos los tipos de flags, sobre x identificador

por ejemplo, quiero consultar un elemento, pero puede suceder que ya fue consultado y no necesite ir 
a la base de datos, que haya sido eliminado de la db o que no haya exisitido nunca, 
que este almacenado en memoria cache pero que no este actualizado y requiera el ultimo registro, o que no este 
en la memoria cache, y necesite consultarlo en la base de datos, como resuelvo todo esto?

falgs count?
	count read? 
	count update?

READ
	IF EXISTS ELEMENT (CRD = 1 AND RDE = 1)
		GET ELEMENT REDIS
		CRDE += 1 (asignamos una lectura al element)
		RETURN ELEMENT
	IF EXISTS ELEMENT (CRD = 1 AND RDE = 1 AND UPD = 1)
		IR DB
			GET ELEMENT MONGO
			UPDATE ELEMENT EN REDIS
			CRDE += 1 (asignamos una lectura al elemento)
			UPD = 0
			RETURN ELEMENT
	IF EXISTS ELEMENT (CRD = 1 AND RDE = 0)
		IR DB
			GET ELEMENT MONGO
			SAVE ELEMENT EN REDIS
			CRDE += 1 (asignamos una lectura al elemento)
			RDE = 1 (tildamos la bandera en prendida para decir que el elemento esta en cache)
			RETURN ELEMENT
	

actualizo elemento, y le doy un flag que fue actualizado, entonces debo decir que la proxima ves 
que consulte, lo haga directo a al base de datos y actualize el elemento en el cache de redis

UPDATE
	ACTUALIZAMOS ELEMENTO EN MONGODB
	IF EXISTS ELEMENTO IN REDIS
		UPD = 1
		CUPD +=1
		RETURN TRUE


Si voy a elimiar un elemento, lo retiro de mongo y luego de redis pero tildo con un flag de eliminado
el elemento de redis

DELETE
	IF EXISTS ELEMENT
		DELETE ELEMENT EN MONGO
		DELETE ELEMENT EN REDIS
		DLT = 1

OPERACION DE CONSULTA
	COMO GUARDO N CANTIDAD DE ELEMNTOS EN REDIS?
	CUANDO RETIRO DE MONGO, CON UN FIND() ME DA TODOS LOS ELEMENTOS
	LOS RECORRO CON UN ITERADOR, Y VOY SACANDO DE A UNO... 

	EL TEMA ES, QUE .. CUANDO QUIERO LEER UNA CONSULTA YA EFECTUADA
	VOY A IR DIRECTO A REDIS, Y REDIS QUE VA A DARME? ELEMENTO X ELEMENTO? 
	A TODOS LOS ELEMENTOS JUNTOS? SI ES ASI, TENGO QUE DARLE TODO A
	PARA LUEGO IR ITERANDO UNO POR UNO?

	AVER, MONGO ME DA TODOS LOS ELEMENTOS CON FIND(), FIND({KEY:VALUE}) U OTRO TIPO DE CONSULTA
	SON 2050 ELEMENTOS, PERO YO VOY ITERANDO DE A POCO, ENTONCES VOY ALMACENANDO TODOS EN UNA COLA 
	CUANDO CORTE LA CONSULTA AL ITERADOR, GUARDO LO QUE TENGO EN REDIS? ES UNA SOLUCION ??

	AVER, MONGO ME DA TODOS LOS ELEMENTOS, PERO ITERO O EFECTUO CONSULTAS SOBRE ALGUNOS

	SIMPLE 
		EJEMPLO MONGO ME X ELEMENTOS
		CUENTO LA CANTIDAD DE ELEMTNS OQUE ME DIO
		PERO YO ITERO SOBRE LOS PRIMEROS 50, ENTONCES ESOS 50 LOS VOY METIENDO EN UNA COLA EN REDIS
		Y LE DIGO QUE ITERE SOBRE LOS PRIMEROS 50 Y FALTARON ITERAR UNOS 150 + QUE NO TIENE ALMACENADOS
		ENTONCES LA PROXIMA VES QUE INTENTE ITERERAR, LE PIDO A REDIS LOS 50 ELEMENTOS + LOS OTROS QUE NO ITERE

	FUNCION HASH SOBRE EL NOMBRE?? (no es necesario ya que mongodb nos provee un identificador unico generador
	por una funcion hash ;) )

"""


class wrpMR(MongoClient):

	def __init__(self):
		MongoClient.__init__(self, host="localhost", port=27017)
		self.__r1 = StrictRedis(db=1)
		self.__r2 = StrictRedis(db=2)
		self.__enl = None

	def __hash(self, insert):
		format = str(insert).replace(" ", "")
		endhash = sha1(format).hexdigest()
		return endhash

	def __setflags(self, key):
		"""		
			flag crd = 0 de creacion (se activa cuando se creo un registro en disco)
			flag try = 0 suma intentos creacion de registro
			flag rde = 0 de lectura ( se activa cuando esta disponible en cache un registro y se apgaga cuando se elimina)
			flag crde = 0 counter de lectura +1
			flag upd = 0 update (se activa cuando se actualizo un registro) y se apaga cuando ya esta actualizado en cache
			flag cupd = 0 counter de actualizacion +1
			flag dlt = 0 delete (se activa cuando se elimino un registro)
		"""
		flags = {"crd": 0 ,"try": 0, "rde": 0, "crde": 0, "upd": 0, "cupd": 0, "dlt":0}
		result = self.__r2.hmset(str(key), flags)
		return result
	
	def enlace(self, **kwargs):
		"""
			enlace(db="midb", table="mitable")
		"""

		self.__db = kwargs.get("db")
		self.__cls = kwargs.get("table")
		self.__enl = self[self.__db][self.__cls]

	def created(self, **kwargs):
		"""
			created(insert="miregistro")
		"""
		
		registro = kwargs.get("insert")
		hashkey = self.__hash(registro)
		islive = self.__r2.hexists(hashkey, "crd")
		
		if not islive and self.__enl != None:
			self.__enl.insert(registro) # cuando se haya completado esto de manera exitosa, asignamos flags
			result = self.__setflags(hashkey)
			self.__r2.hset(hashkey, "crd", "1")
		
		elif islive:
			keyflags = self.__r2.hgetall(hashkey)
			if keyflags['crd'] == 1 and keyflags['dlt'] == 0:
				self.__r2.hincrby(hashkey, "try")
			if keyflags['crd'] == 1 and keyflags['dlt'] == 1:
				self.__r2.hincrby(hashkey, "try")

	def read(self, hashkey=None, **kwargs):
		"""
			read(hashkey="ObjectID", read="find_one")
			read(hashkey="ObjectID", read="find")
			read(hashkey="ObjectID", read="find", query={})
		"""
		# 
		# si quiero asignar un tipo de consulta, find({tipo_query})
		# si quiero asginar una consulta total, find()
		# si quiero asignar una consulta unica, find_one()
		# efectuamos la consulta y el tipo y luego enviamos los datos al iterador next()
		# tengo tres tipos de consultas, find() find_one(), find({query}), como cacheo todo?
		# 
		# si hago una consulta entera tomo el hashkey, mediante el full name a quien le pregunto, dame toodo
		# 
		# si hago una consulta entera + query, tomo el hashkey de la db+table+query
		# 
		# 
		exists = self.__r2.hexists(hashkey, "crd")
		read = kwargs.get("read")
		querys = kwargs.get("query")

		flags = self.__r2.hgetall(hashkey)
		update = int(flags['crd']) + int(flags['rde']) + (flags['upd'])
		
		if flags['crd'] == 1 and flags['rde'] == 0:
			registro = self.__enl.find_one({'_id':hashkey})[0]
			self.__r1.set(hashkey, registro)
			self.__r2.hincrby(hashkey, "rde")
			self.__r2.hincrby(hashkey, "crde")

		elif flags['crd'] == 1 and flags['rde'] == 1 and flags['upd'] == 0:
			registro = self.__r1.get(hashkey)
			self.__r2.hincrby(hashkey, "crde")
			return registro
		
		elif update is 3:
			newregistro = self.__enl.find_one({'_id':hashkey})[0]
			self.__r1.set(hashkey, newregistro)
			self.__r2.hincrby(hashkey, "crde")
			self.__r2.hset(hashkey, 'upd', '0')
			return newregistro

	def next(self):
		pass

	def update(self):
		pass

	def delete(self):
		pass

	def exit(self):
		pass