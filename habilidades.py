import shlex

class Habilidad:
    '''Abstracción del concepto de habilidad en un asistente.'''

    def __init__(self, nombre, descripcion=None):
        self.nombre = nombre
        self.descripcion = descripcion or self.__doc__

    def invocar(self):
        print(f'Se ha invocado la habilidad {self.nombre}')

    def ayuda(self):
        texto = (self.invocar.__doc__) or 'No hay ayuda específica'
        print(texto)


class Divisas(Habilidad):
    '''Conversión de divisas'''
    def __init__(self, *args, tasa=0.85, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasa = tasa

    def invocar(self, cantidad):
        '''Convertir una cantidad la divisa original a la divisa objetivo'''
        return round(float(cantidad) * self.tasa, 2)


class HabilidadCompleja(Habilidad):
    '''Un tipo de habilidad que permite invocar varios sub-comandos'''

    def subcomandos(self):
        '''
        Devuelve un diccionario de subcomandos a funciones.
        
        p.e.:
            {
            'insertar': self.insertar_producto,
            'borrar': self.borrar_producto,
            }
        '''
        return {}

    def invocar(self, subcomando, *args):
        self.subcomandos()[subcomando](*args)

    def ayuda(self):
        print('Comando:\t', self.nombre)
        print('Descripción:\t', self.descripcion)
        print('Subcomandos:')
        for sub, func in self.subcomandos().items():
            print(f'\t{sub}: {func.__doc__ or "No hay ayuda disponible"}')

class ListaDeLaCompra(HabilidadCompleja):
  '''Gestión muy simple de lista de la compra'''

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
    self.productos.append(producto)

  def listar(self):
    '''Mostrar el listado de productos'''
    for ix, producto in enumerate(self.productos):
      print(f'{ix}: {producto}')

  def borrar(self, numero):
    '''Borrar un producto'''
    self.productos.pop(int(numero))

  def cantidad(self):
    '''Mostrar el número de productos en la lista'''
    return len(self.productos)

class Menu:
    '''Menú interactivo de gestión de habilidades.'''

    def __init__(self, habilidades):
        self.habilidades = {}
        for hab in habilidades:
            self.habilidades[hab.nombre] = hab

    def ayuda(self, comando=None):
        '''
        Muestra ayuda del uso del menú. Si no se especifica una habilidad,
        se muestra la ayuda general. Esta ayuda general muestra la lista
        de habilidades, una por línea, y la descripción de cada habilidad.

        Si se especifica una habilidad, se muestra su ayuda específica.
        '''
        if not comando:
            print('Habilidades disponibles:')
            for hab in self.habilidades.values():
                print(f'\t{hab.nombre}:\t{hab.descripcion}')
            return
        if comando not in self.habilidades:
            print(f'Habilidad no encontrada: {comando}')
            return
        self.habilidades[comando].ayuda()

    def lanzar(self):
        '''Recibe instrucciones del usuario en bucle.'''
        while True:
            line = input('> ')
            if self.ejecutar(line):
                break

    def convertir_linea(self, linea):
        comando, *args = shlex.split(linea)
        return comando, args

    def ejecutar(self, linea):
        '''
        Recibe una línea del usuario y ejecuta la acción requerida

        Devuelve True cuando se desea parar la ejecución.
        '''
        comando, args = self.convertir_linea(linea)

        if comando == 'salir':
            return True
        elif comando == 'ayuda':
            if len(args) < 1:
                self.ayuda()
                return False

            hab = args[0]
            self.ayuda(hab)
            return

        if comando not in self.habilidades:
            print('Comando no aceptado: ', comando)
            self.ayuda()
            return False

        hab = self.habilidades[comando]
        res = hab.invocar(*args)
        if res:
            print(res)

    def emular(self, line):
        '''Ejecuta una línea, mostrando por pantalla el comando'''
        print('>', line)
        self.ejecutar(line)


class MenuComas(Menu):
    def convertir_linea(self, linea):
        comando, *args = linea.split(',')
        return comando, args

class MenuPrompt(Menu):
    def __init__(self, *args, prompt='>', **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = prompt

    def emular(self, linea):
        '''Ejecuta una línea, mostrando por pantalla el comando'''
        print(self.prompt, linea)
        self.ejecutar(linea)

    def lanzar(self):
        '''Recibe instrucciones del usuario en bucle.'''
        while True:
            line = input(self.prompt + ' ')
            if self.ejecutar(line):
                break

class MenuPreguntas(Menu):
    def convertir_linea(self, linea):
        comando = linea.strip()
        ix = 0
        args = []
        while True:
            arg = input(f'Argumento {ix}: ')
            if not arg:
                return comando, args
            args.append(arg)
            ix += 1

def prueba_menu_simple():
    habilidades = [
        Divisas('bitcoin2euro', tasa=49929.38, descripcion='Conversión de bitcoins a euros'),
        Divisas('euro2bitcoin', tasa=1/49929.38, descripcion='Conversión de euros a bitcoins'),
    ]
    m = Menu(habilidades)
    m.emular('ayuda')
    m.emular('bitcoin2euro 100')
    m.emular('euro2bitcoin 100')
    m.emular('ayuda noexiste')
    m.emular('ayuda bitcoin2euro')

def prueba_menu_complejas():
    habilidades = [
        Divisas('bitcoin2euro', tasa=49929.38),
        Divisas('euro2bitcoin', tasa=1/49929.38),
        ListaDeLaCompra('listadelacompra', 'Gestión de la lista de la compra')
    ]
    m = Menu(habilidades)
    m.emular('ayuda')
    m.emular('ayuda listadelacompra')
    m.emular('listadelacompra insertar "1 kg de plátanos canarios"')
    m.emular('listadelacompra insertar "Pimientos"')
    m.emular('listadelacompra listar')
    m.emular('listadelacompra borrar 0')
    m.emular('listadelacompra listar')

if __name__ == '__main__':
    prueba_menu_simple()
    print('#'*10)
    prueba_menu_complejas()
    
