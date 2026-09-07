"""
Maxi cream - Heladería y cafetería
Clases Producto y Pedido con operaciones CRUD.
"""


class Producto:
    # Lista de clase: aquí quedan registrados todos los productos (simula una base de datos)
    productos_registrados = []

    def __init__(self, codigo, nombre, categoria, precio, cantidad_disponible):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.cantidad_disponible = cantidad_disponible

    # CREATE
    def registrar_producto(self):
        Producto.productos_registrados.append(self)
        print(f"Producto '{self.nombre}' registrado correctamente.")

    # READ
    @classmethod
    def consultar_producto(cls, codigo):
        for producto in cls.productos_registrados:
            if producto.codigo == codigo:
                producto.descripcion()
                return producto
        print(f"No se encontró ningún producto con código {codigo}.")
        return None

    # UPDATE
    def actualizar_producto(self, nombre=None, categoria=None, precio=None, cantidad_disponible=None):
        if nombre is not None:
            self.nombre = nombre
        if categoria is not None:
            self.categoria = categoria
        if precio is not None:
            self.precio = precio
        if cantidad_disponible is not None:
            self.cantidad_disponible = cantidad_disponible
        print(f"Producto '{self.nombre}' actualizado correctamente.")

    # DELETE
    def eliminar_producto(self):
        if self in Producto.productos_registrados:
            Producto.productos_registrados.remove(self)
            print(f"Producto '{self.nombre}' eliminado correctamente.")
        else:
            print(f"El producto '{self.nombre}' no estaba registrado.")

    def descripcion(self):
        print("Información del producto")
        print("Código:", self.codigo)
        print("Nombre:", self.nombre)
        print("Categoría:", self.categoria)
        print("Precio: $", self.precio)
        print("Cantidad disponible:", self.cantidad_disponible)


class Pedido:
    # Lista de clase: aquí quedan registrados todos los pedidos
    pedidos_registrados = []

    def __init__(self, codigo, fecha, hora):
        self.codigo = codigo
        self.fecha = fecha
        self.hora = hora
        self.productos_seleccionados = []  # lista de objetos Producto
        self.total_pedido = 0
        self.estado_pedido = "pendiente"

    # CREATE
    def registrar_pedido(self):
        Pedido.pedidos_registrados.append(self)
        print(f"Pedido {self.codigo} registrado correctamente.")

    # READ
    @classmethod
    def consultar_pedido(cls, codigo):
        for pedido in cls.pedidos_registrados:
            if pedido.codigo == codigo:
                pedido.descripcion()
                return pedido
        print(f"No se encontró ningún pedido con código {codigo}.")
        return None

    # UPDATE (agregar/quitar productos y recalcular el total)
    def agregar_producto(self, producto, cantidad=1):
        for _ in range(cantidad):
            self.productos_seleccionados.append(producto)
        self.calcular_total()
        print(f"Se agregó '{producto.nombre}' x{cantidad} al pedido {self.codigo}.")

    def eliminar_producto_del_pedido(self, producto):
        if producto in self.productos_seleccionados:
            self.productos_seleccionados.remove(producto)
            self.calcular_total()
            print(f"Se eliminó '{producto.nombre}' del pedido {self.codigo}.")
        else:
            print(f"'{producto.nombre}' no estaba en el pedido {self.codigo}.")

    def calcular_total(self):
        self.total_pedido = sum(p.precio for p in self.productos_seleccionados)
        return self.total_pedido

    def confirmar_pedido(self):
        self.estado_pedido = "confirmado"
        print(f"Pedido {self.codigo} confirmado. Total: ${self.total_pedido}")

    # DELETE
    def cancelar_pedido(self):
        self.estado_pedido = "cancelado"
        if self in Pedido.pedidos_registrados:
            Pedido.pedidos_registrados.remove(self)
        print(f"Pedido {self.codigo} cancelado.")

    def descripcion(self):
        print("Información del pedido")
        print("Código:", self.codigo)
        print("Fecha:", self.fecha)
        print("Hora:", self.hora)
        print("Productos:", [p.nombre for p in self.productos_seleccionados])
        print("Total: $", self.total_pedido)
        print("Estado:", self.estado_pedido)


# ------------------ DEMOSTRACIÓN ------------------

# CRUD de Producto
helado = Producto(1, "Helado de chocolate", "Helado", 8000, 20)
malteada = Producto(2, "Malteada de fresa", "Malteada", 12000, 15)
ensalada = Producto(3, "Ensalada de frutas", "Ensalada", 15000, 10)

helado.registrar_producto()
malteada.registrar_producto()
ensalada.registrar_producto()

print("\n=== CONSULTAR PRODUCTO ===")
Producto.consultar_producto(1)

print("\n=== ACTUALIZAR PRODUCTO ===")
helado.actualizar_producto(precio=9000)

print("\n=== ELIMINAR PRODUCTO ===")
ensalada.eliminar_producto()

print("\n=== LISTA FINAL DE PRODUCTOS ===")
for producto in Producto.productos_registrados:
    producto.descripcion()

# CRUD de Pedido
print("\n=== CRUD DE PEDIDO ===")
pedido1 = Pedido(101, "05/09/2026", "3:00 PM")
pedido1.registrar_pedido()
pedido1.agregar_producto(helado, 2)
pedido1.agregar_producto(malteada, 1)
pedido1.confirmar_pedido()
Pedido.consultar_pedido(101)

# ---------- Taller 3: objetos en una lista ----------

lista = []
lista.append(Producto(1, "Helado de chocolate", "Helado", 8000, 20))
lista.append(Producto(2, "Malteada de fresa", "Malteada", 12000, 15))
lista.append(Producto(3, "Ensalada de frutas", "Ensalada", 15000, 10))

for obj in lista:
    obj.descripcion()

# ---------- Taller 4: CRUD completo ----------

inventario = []

# CREAR (al menos 2 objetos)
inventario.append(Producto(1, "Helado de chocolate", "Helado", 8000, 20))
inventario.append(Producto(2, "Malteada de fresa", "Malteada", 12000, 15))

print("=== CREAR ===")
for p in inventario:
    p.descripcion()

# LEER (ya se hizo arriba con el for, pero lo dejamos explícito)
print("\n=== LEER ===")
for p in inventario:
    p.descripcion()

# ACTUALIZAR (buscar uno y cambiarle un dato)
print("\n=== ACTUALIZAR ===")
for p in inventario:
    if p.nombre == "Helado de chocolate":
        p.actualizar_producto(precio=9000)

print("Lista después de actualizar:")
for p in inventario:
    p.descripcion()

# BORRAR (eliminar uno de la lista)
print("\n=== BORRAR ===")
for p in inventario:
    if p.nombre == "Malteada de fresa":
        inventario.remove(p)
        break

print("Lista después de borrar:")
for p in inventario:
    p.descripcion()

# ---------- Taller 5: Herencia ----------

class Helado(Producto):
    def __init__(self, codigo, nombre, categoria, precio, cantidad_disponible, sabor):
        super().__init__(codigo, nombre, categoria, precio, cantidad_disponible)  # arma la parte de Producto
        self.sabor = sabor  # atributo propio

    def agregar_topping(self, topping):  # método propio
        print(f"Se agregó '{topping}' al helado de {self.sabor}.")


class Bebida(Producto):
    def __init__(self, codigo, nombre, categoria, precio, cantidad_disponible, tamano):
        super().__init__(codigo, nombre, categoria, precio, cantidad_disponible)  # arma la parte de Producto
        self.tamano = tamano  # atributo propio

    def servir(self):  # método propio
        print(f"Sirviendo {self.nombre}, tamaño {self.tamano}.")


# Crear un objeto de cada subclase
helado1 = Helado(4, "Helado de vainilla", "Helado", 8000, 20, "Vainilla")
bebida1 = Bebida(5, "Malteada de fresa", "Malteada", 12000, 15, "Grande")

print("\n=== TALLER 5: HELADO ===")
helado1.descripcion()             # heredado de Producto
helado1.agregar_topping("chispas de colores")  # propio de Helado

print("\n=== TALLER 5: BEBIDA ===")
bebida1.descripcion()             # heredado de Producto
bebida1.servir()                  # propio de Bebida

# ---------- Taller 6: CRUD de Clientes ----------

class Cliente:
    def __init__(self, nombre, telefono, cedula):
        self.nombre = nombre
        self._telefono = telefono  # encapsulado
        self.cedula = cedula
        self.compras_totales = 0

    def __str__(self):
        return f"{self.nombre} (CC {self.cedula}) - compras: ${self.compras_totales}"


clientes = []

# CREAR
clientes.append(Cliente("Laura Gómez", "3001112233", "1020304050"))
clientes.append(Cliente("Pedro Ruiz", "3009998877", "1030405060"))

print("=== CREAR ===")
for c in clientes:
    print(c)

# LEER
print("\n=== LEER ===")
for c in clientes:
    print(c)

# ACTUALIZAR
print("\n=== ACTUALIZAR ===")
for c in clientes:
    if c.cedula == "1020304050":
        c.compras_totales += 45000

print("Lista después de actualizar:")
for c in clientes:
    print(c)

# BORRAR
print("\n=== BORRAR ===")
for c in clientes:
    if c.cedula == "1030405060":
        clientes.remove(c)
        break

print("Lista después de borrar:")
for c in clientes:
    print(c)
