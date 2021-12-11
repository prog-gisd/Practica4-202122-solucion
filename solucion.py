import pickle
import os
import csv
import json
import shutil

from datetime import datetime

from habilidades import HabilidadCompleja

FICHERO_PICKLE = 'estado.pickle'
FICHERO_JSON = 'estado.json'

def leer_estado_pickle(fichero=FICHERO_PICKLE):
    if not os.path.exists(fichero):
        print('no existe el fichero', fichero)
        return {}

    with open(fichero, 'rb') as f:
        return pickle.load(f)

def guardar_estado_pickle(datos, fichero=FICHERO_PICKLE):
    with open(fichero, 'wb') as f:
        pickle.dump(datos, f)

def leer_estado_json(fichero=FICHERO_JSON):
    '''Recupera el estado desde un JSON'''
    if not os.path.exists(fichero):
        print('no existe el fichero', fichero)
        return {}

    with open(fichero, 'r', encoding='utf8') as f:
        return json.load(f)
    

def guardar_estado_json(estado, fichero=FICHERO_JSON):
    '''Guarda el estado proporcionado en un JSON'''
    with open(fichero, 'w', encoding='utf8') as f:
        json.dump(estado, f)

class Almacen:
    '''Clase genérica para los almacenes de estado'''

    def guardar(self, estado):
        '''Guarda el valor del estado.'''
        raise NotImplementedError

    def leer(self, defecto=None):
        '''Devuelve el valor guardado del estado'''
        raise NotImplementedError


class EnMemoria(Almacen):
    '''Guarda valores en memoria (sin persistencia en disco)'''
    def __init__(self):
        self.estado = {}

    def guardar(self, estado):
        self.estado = estado.copy()

    def leer(self, defecto=None):
        return self.estado or defecto


class AlmacenFichero(Almacen):
    '''Clase para heredar en los almacenes que usen un fichero'''
    def __init__(self, fichero):
        self.fichero = fichero

class AlmacenPickle(Almacen):
    def __init__(self, fichero):
        self.fichero = fichero

    def guardar(self, estado):
        return guardar_estado_pickle(estado, fichero=self.fichero)

    def leer(self, defecto=None):
        return leer_estado_pickle(fichero=self.fichero) or defecto


class AlmacenJSON(Almacen):

    def __init__(self, fichero):
        self.fichero = fichero

    def guardar(self, estado):
        with open(self.fichero, 'w') as f:
            json.dump(estado, f)

    def leer(self, defecto={}):
        if not os.path.exists(self.fichero):
            return defecto

        with open(self.fichero, 'r') as f:
            return json.load(f)


class MultiAlmacen(Almacen):
    def __init__(self, almacenes):
        self.almacenes = almacenes

    def guardar(self, estado):
        for almacen in self.almacenes:
            almacen.guardar(estado)

    def leer(self, *args, **kwargs):
        return self.almacenes[0].leer(*args, **kwargs)


class AlmacenBackup(Almacen):

    def __init__(self, interno):
        '''Tipo debe ser una subclase de Almacen que tenga un atributo fichero'''
        self.interno = interno
        self.copias = []

    def guardar(self, estado):
        fecha = datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f')
        fichero_copia = self.interno.fichero + '_copia_' + fecha
        if os.path.exists(self.interno.fichero):
            shutil.copyfile(self.interno.fichero, fichero_copia)
            self.copias.append(fichero_copia)
        self.interno.guardar(estado)

    def leer(self, *args, **kwargs):
        return self.interno.leer(*args, **kwargs)

class ListaDeLaCompra(HabilidadCompleja):
  '''Gestión de lista de la compra que incluye excepciones'''

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.productos = []

  def subcomandos(self):
    return {
      'insertar': self.insertar,
      'borrar': self.borrar,
      'listar': self.listar,
      'cantidad': self.cantidad,
      }

  def insertar(self, producto):
    '''Insertar un producto nuevo'''
    if producto == '' or producto == None:
        raise Exception
    self.productos.append(producto)

  def listar(self):
    '''Mostrar el listado de productos'''
    for ix, producto in enumerate(self.productos):
      print(f'{ix}: {producto}')

  def borrar(self, numero):
    '''Borrar un producto'''
    if numero < 0 or numero >= len(self.productos):
        raise Exception
    self.productos.pop(int(numero))

  def cantidad(self):
    '''Mostrar el número de productos en la lista'''
    return len(self.productos)

class ListaDeLaCompraAlmacenada(ListaDeLaCompra):

    def __init__(self, *args, almacen=EnMemoria, **kwargs):
        super().__init__(*args, **kwargs)
        self.almacenamiento = almacen
        productos = self.almacenamiento.leer(defecto=[])
        self.productos = productos

    def insertar(self, producto):
        super().insertar(producto)
        self.almacenamiento.guardar(self.productos)

    def borrar(self, numero):
        super().borrar(numero)
        self.almacenamiento.guardar(self.productos)
