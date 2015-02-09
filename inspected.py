#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://pymotw.com/2/contents.html
# importar o tener modulo de cacheo en la misma carpeta

# --------------------------------- #
# ESTUDIAR LOS MODULOS RELACIONADOS #
# **  Python Runtime Services    ** #
# _________________________________ #

import difflib
import inspect
import itertools
import weakref
import pdb
import warnings
import string
import cmd
import functools
import collections
import json
import types
import traceback
import os

'''
    Obtener las clases de un modulo y sus (padres) o que heredan.
    Obtener los metodos de una clase.
    Obtener las variables globales de configuracion.
    Obtener las funciones del modulo.
    
    Armar un objeto donde, segun un arbol se explique la estructura del modulo.
    Guardar todo en un archivo JSON
'''

TYPES = ['BooleanType', 'BufferType', 'BuiltinFunctionType', 'BuiltinMethodType', 'ClassType', 'CodeType', 'ComplexType', 'DictProxyType', 'DictType', 'DictionaryType', 'EllipsisType', 'FileType', 'FloatType', 'FrameType', 'FunctionType', 'GeneratorType', 'GetSetDescriptorType', 'InstanceType', 'IntType', 'LambdaType', 'ListType', 'LongType', 'MemberDescriptorType', 'MethodType', 'ModuleType', 'NoneType', 'NotImplementedType', 'ObjectType', 'SliceType', 'StringType', 'StringTypes', 'TracebackType', 'TupleType', 'TypeType', 'UnboundMethodType', 'UnicodeType', 'XRangeType', '__builtins__', '__doc__', '__file__', '__name__', '__package__']


# le podemos pasar como parametros, un modulo, una funcion, una clase, una variable

#inspect_all = insobj(fun=[function, functionN], cls=[class, classN], mod=[module, moduleN])

class insFun(object):
    '''
        inspect_fun = insFun(fun=[function1, function2, functionN])
    '''
    def __init__(self, fun=[]):
        self.funciones = [f for f in fun if isinstance(f, types.FunctionType)]


class insCls(insFun):
    '''
        inspect_cls = insCls(cls=[class1, class2, classN])
    '''
    def __init__(self, cls=[]):
        self.clases = [c for c in cls if isinstance(c, types.ClassType) or isinstance(c, types.InstanceType)]


class inspMod(insCls):
    '''
        inspect_mod = insobj(mod=[mod1, mod2], maxlen=2)
        
    '''
    def __init__(self, mod=[], maxlen=1):
        #  FILTROS DE CREACION
        if maxlen == 1:
            self.modulo = [m for m in mod if isinstance(m, types.ModuleType)]
            if not self.modulo:
                raise "Error, ningun modulo para analisar."
            else:
                self.__len = len(self.modulo)
                self.__analisis = {}
                self.__cls = {}
                self.__mod = {}
                self.__fun = {}
                self.__dic = {}
                if hasattr(self.modulo[self.__len], "__file__"):
                    self.metadata(self.modulos[0].__file__)
        else:
            raise "Only maxlen=1 ."

    def metadata(self, filename):
        # OBTENEMOS LOS METADATOS DEL MODULO
        try:
            (name, suffix, mode, mtype)  = inspect.getmoduleinfo(filename)
        except TypeError:
            print 'Could not determine module type of %s' % filename
        else:
            mtype_name = { imp.PY_SOURCE:'source',
                           imp.PY_COMPILED:'compiled',
                           }.get(mtype, mtype)
            
            mode_description = { 'rb':'(read-binary)',
                                 'U':'(universal newline)',
                                 }.get(mode, '')
            self.name = name
            self.suffix = suffix
            self.mode_description = (mode, mode_description)
            self.mtype_name = mtype_name
    
    def inspect(self):
        # OBTENEMOS LAS FUNCIONES, CLASES Y OTROS MODULOS, DEL MODULO
        for name, data in inspect.getmembers(self.modulo[self.__len]):
            if name == '__builtins__':
                continue
            self.__analisis[name] = data
            if isinstance(data, types.FunctionType):
                self.__fun[name] = data
            if isinstance(data, (types.ClassType or types.InstanceType or types.ObjectType)):
                self.__cls[name] = data
            if isinstance(data, types.ModuleType):
                self.__mod[name] = data
            if isinstance(data, (types.DictionaryType or types.DictType)):
                self.__dic[name] = data
            if isinstance(data, types.FileType):
                self.__file[name] = data
            if isinstance(data, types.TracebackType):
                self.__tback[name] = data
    
    def cls_methods(self, cls=None):
        # INTENTAMOS OBTENER TODO LOS METODOS DE TODAS LAS CLASES.
        # ARMAMOS UN DICIONARIO DONDE CADA CLAVE SEA EL NOMBRE DE LA CLASE.
        # CADA VALOR DISPONGA DE OTRO DICIONARIO, CON NOMBRE ( METODO ), VALOR ( TIPO DE METODO )
        if not cls:
            length = len(self.__cls)
            cls = self.__cls
        if isinstance(cls, types.DictionaryType):
            self.__cls_methods = {}            
            for name in cls.keys():
                self.__cls_methods["{0}".format(data)] = dict(inspect.getmembers(self.modulo[0].name, inspect.ismethod))
        else:
            raise "Ninguna clase para Analisar"
    
    def insp_args(self, func=None):
        if not func:
            #SI NO RECIBE NINGUNA FUNCION COMO ARGUMENTO ASIGNARLE UNA FUNCION.
            pass
        # APLICAMOS FILTROS PARA CORROBORAR QUE HAYAMOS RECIBIDO UNA FUNCION DE ARGUMENTO 
        if isinstance(func, (types.FunctionType or types.MethodType)):
            self.argspec = (args, varargs, keywords, defaults) = inspect.getargspec(func)
            args_with_defaults = self.argspec[0][-len(arg_spec[3]):]
            self.args_defaults = zip(args_with_defaults, self.argspec[3])
        else:
            raise "No es una funcion."

    def inject(self, add=None):
        
        #    ARMAR FUNCION QUE INJECTE CODIGO PARA DEBUGEAR DENTRO DE UNA FUNCION
        #    COMO LO HACEMOS?;
        # 1. CONSIGO EL CODIGO,
        # 2. BUSCAMOS EL PUNTO DE INJECION
        # 3. RE-ESCRIBIMOS EL CODIGO
        # 4. GUARDAMOS
        
        if not add:
            self.inje_debug = ["self.log( inspect.getargvalues(inspect.currentframe()) )", "otra1", "otra"]
        else:
            self.inje_debug.append(add)
        
        try:
            listsource = list(inspect.getsourcelines(example.A.get_name))
        except Exception:
            print('If the source file is not available, getsource() and getsourcelines() raise an IOError.')
        
    def get_source(self, func=None, module=None, cls=None):
        
        # RETORNA EL CODIGO FUENTE

        if not func:
            if isinstance(func, (types.MethodType or types.FunctionType)):
                return(types.FunctionType, inspect.getsource(func))

        if not module:
            if isinstance(func, types.ModuleType):
                return(types.ModuleType, inspect.getsource(module))

        if not cls:
            if isinstance(cls, (types.ClassType or types.InstanceType or types.ObjectType)):
                return inspect.getsource(cls)


    def attrs(self, ):
        pass


asd = inspMod(mod=[difflib], maxlen=1)
