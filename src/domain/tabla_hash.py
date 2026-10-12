"""
Tabla hash para indexar la biblioteca musical completa.

Permite guardar y buscar canciones por su identificador (clave) en tiempo
prácticamente constante en el caso promedio, usando encadenamiento para
resolver colisiones (cuando dos claves distintas caen en la misma posición).
"""


class NodoHash:
    def __init__(self, clave, cancion):
        self.clave = clave
        self.cancion = cancion
        self.siguiente = None  # para encadenar varias canciones en la misma cubeta


class TablaHash:
    def __init__(self, capacidad=16):
        self.capacidad = capacidad
        self.cubetas = [None] * capacidad  # cada cubeta es la cabeza de una lista encadenada
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def _indice(self, clave):
        """Convierte la clave en una posición válida dentro de las cubetas."""
        return hash(clave) % self.capacidad

    def insertar(self, clave, cancion):
        """Agrega una canción bajo esa clave, o la actualiza si ya existía. Costo promedio O(1)."""
        i = self._indice(clave)
        nodo = self.cubetas[i]

        while nodo is not None:
            if nodo.clave == clave:
                nodo.cancion = cancion
                return
            nodo = nodo.siguiente

        nuevo = NodoHash(clave, cancion)
        nuevo.siguiente = self.cubetas[i]
        self.cubetas[i] = nuevo
        self._tamano += 1

        if self._tamano / self.capacidad > 0.75:
            self._redimensionar()

    def buscar(self, clave):
        """Busca una canción por su clave. Devuelve None si no existe. Costo promedio O(1)."""
        nodo = self.cubetas[self._indice(clave)]
        while nodo is not None:
            if nodo.clave == clave:
                return nodo.cancion
            nodo = nodo.siguiente
        return None

    def contiene(self, clave):
        return self.buscar(clave) is not None

    def eliminar(self, clave):
        """Elimina una canción por su clave. Devuelve True si existía, False si no."""
        i = self._indice(clave)
        nodo = self.cubetas[i]
        anterior = None
        while nodo is not None:
            if nodo.clave == clave:
                if anterior is None:
                    self.cubetas[i] = nodo.siguiente
                else:
                    anterior.siguiente = nodo.siguiente
                self._tamano -= 1
                return True
            anterior = nodo
            nodo = nodo.siguiente
        return False

    def todas_las_canciones(self):
        """Devuelve todas las canciones guardadas, sin un orden particular."""
        canciones = []
        for cubeta in self.cubetas:
            nodo = cubeta
            while nodo is not None:
                canciones.append(nodo.cancion)
                nodo = nodo.siguiente
        return canciones

    def _redimensionar(self):
        """
        Duplica la cantidad de cubetas cuando la tabla se llena demasiado
        (más del 75% ocupada), para que las búsquedas se mantengan rápidas
        aunque la biblioteca crezca.
        """
        viejas_cubetas = self.cubetas
        self.capacidad *= 2
        self.cubetas = [None] * self.capacidad
        self._tamano = 0

        for cubeta in viejas_cubetas:
            nodo = cubeta
            while nodo is not None:
                self.insertar(nodo.clave, nodo.cancion)
                nodo = nodo.siguiente


if __name__ == "__main__":
    biblioteca = TablaHash()
    biblioteca.insertar("001", {"titulo": "Billie Jean", "artista": "Michael Jackson"})
    biblioteca.insertar("002", {"titulo": "Like a Prayer", "artista": "Madonna"})
    biblioteca.insertar("003", {"titulo": "Purple Rain", "artista": "Prince"})

    print("Buscar '002':", biblioteca.buscar("002")["titulo"])
    print("¿Existe '999'?:", biblioteca.contiene("999"))
    print("Total de canciones:", len(biblioteca))

    biblioteca.eliminar("002")
    print("Después de eliminar '002', ¿existe?:", biblioteca.contiene("002"))
    print("Total de canciones:", len(biblioteca))