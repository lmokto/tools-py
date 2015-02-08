#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import time	

listdir = []
listfile = []
islink = []

def listdirfun(pathexample):

	for f in os.listdir(pathexample):
		file = pathexample+"/"+f
		if os.path.exists(file):
			if os.path.isdir(file):
				print file
				print 'Is Dir?     :', os.path.isdir(file)
				listdir.append(file)
			if os.path.isfile(file):
				print file
				print 'Is File?    :', os.path.isfile(file)
				listfile.append(file)

	print 'Absolute    :', os.path.isabs(file)
	print 'Is Link?    :', os.path.islink(file)
	print 'Mountpoint? :', os.path.ismount(file)
	print 'Link Exists?:', os.path.lexists(file)

def show_file_info(filename):

	if os.path.isfile(filename):
		print filename
		stat_info = os.stat(filename)
		print '\tMode    :', stat_info.st_mode
		print '\tCreated :', time.ctime(stat_info.st_ctime)
		print '\tAccessed:', time.ctime(stat_info.st_atime)
		print '\tModified:', time.ctime(stat_info.st_mtime)


def open_file(filename):

	os.chmod(filename, 420)
	__file = open(filename, "wb")
	__file.write("")
	__file.close()

def main(pathexample):
	
	"""	
	Paso como parametro un carpeta, me da informacion de los archivos, luego abre uno por uno recursivamente, 
	y borra su contenido. 

	python.py cleansync.py "carpeta"
	"""
	
	listdirfun(pathexample)

	for dirpath, dirnames, filenames in os.walk(pathexample):
		print dirpath, dirnames, filenames
		if len(dirnames) >= 0:
			for file in filenames:
				filename = dirpath+"/"+file
				show_file_info(filename)
				open_file(filename)

if __name__ == '__main__':

	pathexample = sys.argv[1]
	main(pathexample)