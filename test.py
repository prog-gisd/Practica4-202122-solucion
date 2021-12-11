import unittest
import sys
import shutil
import os
import io
from contextlib import contextmanager
from glob import glob

from unittest import mock
from functools import partial

from solucion import *




def skipUnlessImplemented(obj):
    if obj in globals():
        return lambda func: func
    return unittest.skip("{} no ha sido implementado".format(obj))


OPTIONAL = False


@contextmanager
def redirected():
    '''
    Context manager para capturar las salida de print (sys.stdout en general).
    Nos va a permitir capturar la salida por pantalla de las funciones del ejercicio.

    Sería mejor separar el código de mostrar_productos en dos funciones: una que devuelve el
    texto, y otra que llama a la primera y lo muestra. Así no haría falta este tipo de
    programación avanzada.
    '''
    saved = sys.stdout
    out = io.StringIO()
    sys.stdout = out
    try:
        yield out
    finally:
        sys.stdout = saved


def red(fun, *args, **kwargs):
    with redirected() as out:
        fun(*args, **kwargs)
    return out.getvalue()

def stub_stdin(testcase_inst, inputs):
    stdin = sys.stdin

    def cleanup():
        sys.stdin = stdin

    testcase_inst.addCleanup(cleanup)
    sys.stdin = io.StringIO(inputs)


TEST_FICHERO = 'test.pickle'
TEST_JSON_FILE = 'test.json'
TEST_CSV_FILE = 'test.csv'
TEST_CARPETA = 'prueba'

FICHEROS_TEST = [TEST_FICHERO,
                 TEST_JSON_FILE,
                 TEST_CSV_FILE,
                 ]

def borrar_estado():
    a_borrar = list(FICHEROS_TEST)

    for backup in glob('*_copia_*'):
        a_borrar.append(backup)

    for f in a_borrar:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists(TEST_CARPETA):
        shutil.rmtree(TEST_CARPETA)

leer_estado_pickle = partial(leer_estado_pickle, fichero=TEST_FICHERO)
guardar_estado_pickle = partial(guardar_estado_pickle, fichero=TEST_FICHERO)

class TestHabilidades(unittest.TestCase):

    def setUp(self):
        borrar_estado()

    def tearDown(self):
        borrar_estado()

    def test_persistencia(self):
        '''Comprobar que las funciones de leer y guardar funcionan'''

        assert not leer_estado_pickle()
        estado = {'productos': [1,2,3,4]}
        guardar_estado_pickle(estado)
        recovered = leer_estado_pickle()
        assert 'productos' in recovered
        assert 3 in recovered['productos']

        estado['contactos'] = {'fernando': 6692312432}

        guardar_estado_pickle(estado)
        recovered = leer_estado_pickle()
        assert 'productos' in recovered
        assert 3 in recovered['productos']
        assert 'contactos' in recovered
        assert 'fernando' in recovered['contactos']
        assert recovered['contactos']['fernando'] == 6692312432

    @skipUnlessImplemented('AlmacenBackup')
    def test_persistencia_backup(self):
        '''Debería haber una copia cada vez que se guarda'''
        interno = AlmacenJSON(fichero=TEST_JSON_FILE)
        p = AlmacenBackup(interno)
        p.guardar({'paso': 0})
        p.guardar({'paso': 1})
        p.guardar({'paso': 2})
        assert len(p.copias) == 2
        copias = glob('*_copia_*')
        assert len(copias) == len(p.copias)

        recuperados = []
        for copia in copias:
            recuperados.append(AlmacenJSON(fichero=copia).leer())
        pasos = list(x['paso'] for x in recuperados)
        assert 0 in pasos
        assert 1 in pasos

    def test_productos_excepciones(self):
        '''La lista de la compra lanza excepciones'''
        t = ListaDeLaCompra(nombre='mis productos')
        self.assertRaises(Exception, t.invocar, 'insertar', '')
        self.assertRaises(Exception, t.invocar, 'borrar', -1)
        t.invocar('insertar', 'prueba')
        assert 'prueba' in t.productos
        self.assertRaises(Exception, t.invocar, 'borrar', 1)

    def test_productos_enmemoria_compartido(self):
        '''El almacenamiento en memoria se puede compartir'''
        p = EnMemoria()
        t = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=p)
        t.invocar('insertar', 'probando')
        assert 'probando' in t.productos
        t2 = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=p)
        assert 'probando' in t2.productos

    def test_productos_enmemoria_independiente(self):
        '''El almacenamiento en memoria no da persistencia'''
        p = EnMemoria()
        t = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=p)
        t.invocar('insertar', 'probando')
        assert 'probando' in t.productos
        p = EnMemoria()
        t2 = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=p)
        assert 'probando' not in t2.productos

    def test_productos_json(self):
        '''El almacenamiento en JSON da persistencia'''
        p = AlmacenJSON(fichero=TEST_JSON_FILE)
        t = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=p)
        t.invocar('insertar', 'probando')
        assert 'probando' in t.productos
        p = AlmacenJSON(fichero=TEST_JSON_FILE)
        t2 = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=p)
        assert 'probando' in t2.productos

    @skipUnlessImplemented('MultiAlmacen')
    def test_productos_multi(self):
        a1 = EnMemoria()
        a2 = EnMemoria()
        multi = MultiAlmacen([a1, a2])
        t = ListaDeLaCompraAlmacenada(nombre='mis productos', almacen=multi)
        t.invocar('insertar', 'probando')
        assert 'probando' in a1.leer('productos')
        assert 'probando' in a2.leer('productos')


if __name__ == '__main__':
    unittest.main(verbosity=2)
