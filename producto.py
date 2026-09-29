"""
Maxi cream - Heladería y cafetería
Clases Producto y Pedido con operaciones CRUD.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

RUTA_BD = Path(__file__).resolve().parent / "productos.db"
METODOS_PAGO = ("efectivo", "tarjeta", "transferencia")


# ============================================================
# CAPA DE DATOS Y LÓGICA (igual que en los Talleres 7 y 8)
# ============================================================

class Producto:
    def __init__(self, codigo, nombre, categoria, precio, cantidad_disponible):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.cantidad_disponible = cantidad_disponible

    @staticmethod
    def crear_tabla():
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                codigo INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                precio REAL NOT NULL,
                cantidad_disponible INTEGER NOT NULL
            )
            """
        )
        conexion.commit()
        conexion.close()

    def guardar(self):
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO productos
                    (codigo, nombre, categoria, precio, cantidad_disponible)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.codigo, self.nombre, self.categoria, self.precio,
                 self.cantidad_disponible),
            )
            conexion.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conexion.close()

    def actualizar(self, nuevo_precio, nueva_cantidad):
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE productos SET precio = ?, cantidad_disponible = ? WHERE codigo = ?",
            (nuevo_precio, nueva_cantidad, self.codigo),
        )
        conexion.commit()
        conexion.close()
        self.precio = nuevo_precio
        self.cantidad_disponible = nueva_cantidad

    def eliminar(self):
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE codigo = ?", (self.codigo,))
        conexion.commit()
        conexion.close()

    @staticmethod
    def listar_todos():
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT codigo, nombre, categoria, precio, cantidad_disponible "
            "FROM productos ORDER BY codigo"
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Producto(*fila) for fila in filas]

    @staticmethod
    def consultar_por_codigo(codigo):
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT codigo, nombre, categoria, precio, cantidad_disponible "
            "FROM productos WHERE codigo = ?",
            (codigo,),
        )
        fila = cursor.fetchone()
        conexion.close()
        return Producto(*fila) if fila else None

    @staticmethod
    def siguiente_codigo():
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        cursor.execute("SELECT MAX(codigo) FROM productos")
        maximo = cursor.fetchone()[0]
        conexion.close()
        return (maximo or 0) + 1


class Factura:
    """COMPOSICIÓN: solo la crea un Pedido, nunca se crea por fuera."""

    def __init__(self, codigo_pedido, detalle, total, metodo_pago):
        self.codigo_pedido = codigo_pedido
        self.detalle = list(detalle)
        self.total = total
        self.metodo_pago = metodo_pago

    def texto(self):
        lineas = [f"--- Factura pedido #{self.codigo_pedido} ---"]
        for producto, cantidad in self.detalle:
            lineas.append(
                f"{producto.nombre} x{cantidad}: ${producto.precio * cantidad:,.0f}"
            )
        lineas.append(f"Total: ${self.total:,.0f}")
        lineas.append(f"Método de pago: {self.metodo_pago}")
        return "\n".join(lineas)


class Pedido:
    _contador = 0  # genera el código de cada pedido nuevo

    def __init__(self):
        Pedido._contador += 1
        self.codigo = Pedido._contador
        self.detalle = []  # AGREGACIÓN: lista de (Producto, cantidad)
        self.total = 0
        self.estado = "pendiente"
        self.metodo_pago = None
        self.factura = None  # COMPOSICIÓN

    def agregar_producto(self, producto, cantidad):
        self.detalle.append((producto, cantidad))
        self.calcular_total()

    def calcular_total(self):
        self.total = sum(p.precio * c for p, c in self.detalle)
        return self.total

    def confirmar(self, metodo_pago):
        """Valida inventario, descuenta stock y marca el pedido confirmado.

        Devuelve (True, mensaje) o (False, motivo del rechazo).
        """
        if not self.detalle:
            return False, "El pedido no tiene productos."
        if metodo_pago not in METODOS_PAGO:
            return False, "Selecciona un método de pago válido."

        for producto, cantidad in self.detalle:
            actual = Producto.consultar_por_codigo(producto.codigo)
            if actual is None or cantidad > actual.cantidad_disponible:
                return False, f"No hay suficiente inventario de '{producto.nombre}'."

        for producto, cantidad in self.detalle:
            actual = Producto.consultar_por_codigo(producto.codigo)
            actual.actualizar(actual.precio, actual.cantidad_disponible - cantidad)

        self.metodo_pago = metodo_pago
        self.estado = "confirmado"
        return True, f"Pedido #{self.codigo} confirmado. Total: ${self.total:,.0f}"

    def generar_factura(self):
        if self.estado != "confirmado":
            return None
        self.factura = Factura(self.codigo, self.detalle, self.total, self.metodo_pago)
        return self.factura


# ============================================================
# INTERFAZ GRÁFICA
# ============================================================

class PestañaProductos(ttk.Frame):
    """CRUD visual sobre la tabla productos."""

    def __init__(self, master):
        super().__init__(master, padding=10)
        self.codigo_seleccionado = None
        self._construir_formulario()
        self._construir_tabla()
        self.refrescar()

    def _construir_formulario(self):
        form = ttk.LabelFrame(self, text="Datos del producto", padding=10)
        form.pack(fill="x", pady=(0, 10))

        self.var_nombre = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_precio = tk.StringVar()
        self.var_cantidad = tk.StringVar()

        campos = [
            ("Nombre", self.var_nombre),
            ("Categoría", self.var_categoria),
            ("Precio", self.var_precio),
            ("Cantidad disponible", self.var_cantidad),
        ]
        for i, (etiqueta, var) in enumerate(campos):
            ttk.Label(form, text=etiqueta).grid(row=0, column=i * 2, sticky="w", padx=4)
            ttk.Entry(form, textvariable=var, width=16).grid(row=0, column=i * 2 + 1, padx=4)

        botones = ttk.Frame(form)
        botones.grid(row=1, column=0, columnspan=8, pady=(10, 0))
        ttk.Button(botones, text="Guardar nuevo", command=self.guardar_nuevo).pack(side="left", padx=4)
        ttk.Button(botones, text="Actualizar seleccionado", command=self.actualizar_seleccionado).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar seleccionado", command=self.eliminar_seleccionado).pack(side="left", padx=4)
        ttk.Button(botones, text="Limpiar formulario", command=self.limpiar).pack(side="left", padx=4)

    def _construir_tabla(self):
        columnas = ("codigo", "nombre", "categoria", "precio", "cantidad")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=12)
        encabezados = {
            "codigo": "Código", "nombre": "Nombre", "categoria": "Categoría",
            "precio": "Precio", "cantidad": "Cantidad disponible",
        }
        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=130 if col != "nombre" else 220)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._cargar_seleccion)

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in Producto.listar_todos():
            self.tabla.insert("", "end", iid=p.codigo,
                               values=(p.codigo, p.nombre, p.categoria,
                                       f"{p.precio:,.0f}", p.cantidad_disponible))
        # avisar a la pestaña de pedidos que el inventario cambió
        if hasattr(self.master.master, "pestaña_pedidos"):
            self.master.master.pestaña_pedidos.refrescar_inventario()

    def _cargar_seleccion(self, _evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        codigo = int(seleccion[0])
        producto = Producto.consultar_por_codigo(codigo)
        if producto is None:
            return
        self.codigo_seleccionado = producto.codigo
        self.var_nombre.set(producto.nombre)
        self.var_categoria.set(producto.categoria)
        self.var_precio.set(str(producto.precio))
        self.var_cantidad.set(str(producto.cantidad_disponible))

    def _leer_formulario(self):
        nombre = self.var_nombre.get().strip()
        categoria = self.var_categoria.get().strip()
        try:
            precio = float(self.var_precio.get())
            cantidad = int(self.var_cantidad.get())
        except ValueError:
            messagebox.showerror("Datos inválidos", "Precio y cantidad deben ser números.")
            return None
        if not nombre or not categoria:
            messagebox.showerror("Datos incompletos", "Nombre y categoría son obligatorios.")
            return None
        return nombre, categoria, precio, cantidad

    def guardar_nuevo(self):
        datos = self._leer_formulario()
        if datos is None:
            return
        nombre, categoria, precio, cantidad = datos
        codigo = Producto.siguiente_codigo()
        producto = Producto(codigo, nombre, categoria, precio, cantidad)
        if producto.guardar():
            messagebox.showinfo("Listo", f"Producto '{nombre}' guardado con código {codigo}.")
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showerror("Error", "No se pudo guardar (código repetido).")

    def actualizar_seleccionado(self):
        if self.codigo_seleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto en la tabla primero.")
            return
        datos = self._leer_formulario()
        if datos is None:
            return
        _, _, precio, cantidad = datos
        producto = Producto.consultar_por_codigo(self.codigo_seleccionado)
        producto.actualizar(precio, cantidad)
        messagebox.showinfo("Listo", f"Producto '{producto.nombre}' actualizado.")
        self.refrescar()

    def eliminar_seleccionado(self):
        if self.codigo_seleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto en la tabla primero.")
            return
        producto = Producto.consultar_por_codigo(self.codigo_seleccionado)
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{producto.nombre}'?"):
            producto.eliminar()
            self.limpiar()
            self.refrescar()

    def limpiar(self):
        self.codigo_seleccionado = None
        for var in (self.var_nombre, self.var_categoria, self.var_precio, self.var_cantidad):
            var.set("")
        self.tabla.selection_remove(self.tabla.selection())


class PestañaPedidos(ttk.Frame):
    """Arma un pedido con productos del inventario (agregación), lo
    confirma (descuenta stock) y genera su factura (composición)."""

    def __init__(self, master):
        super().__init__(master, padding=10)
        self.pedido_actual = Pedido()
        self._construir_inventario()
        self._construir_pedido()
        self.refrescar_inventario()

    def _construir_inventario(self):
        marco = ttk.LabelFrame(self, text="Inventario disponible", padding=10)
        marco.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columnas = ("codigo", "nombre", "precio", "stock")
        self.tabla_inventario = ttk.Treeview(marco, columns=columnas, show="headings", height=14)
        for col, txt in zip(columnas, ("Código", "Nombre", "Precio", "Stock")):
            self.tabla_inventario.heading(col, text=txt)
            self.tabla_inventario.column(col, width=90 if col != "nombre" else 200)
        self.tabla_inventario.pack(fill="both", expand=True)

        fila = ttk.Frame(marco)
        fila.pack(fill="x", pady=(8, 0))
        ttk.Label(fila, text="Cantidad:").pack(side="left")
        self.var_cantidad = tk.StringVar(value="1")
        ttk.Entry(fila, textvariable=self.var_cantidad, width=6).pack(side="left", padx=6)
        ttk.Button(fila, text="Agregar al pedido →", command=self.agregar_al_pedido).pack(side="left", padx=6)

    def _construir_pedido(self):
        marco = ttk.LabelFrame(self, text="Pedido actual", padding=10)
        marco.pack(side="left", fill="both", expand=True)

        self.etiqueta_codigo = ttk.Label(marco, text=f"Pedido #{self.pedido_actual.codigo}",
                                          font=("Segoe UI", 10, "bold"))
        self.etiqueta_codigo.pack(anchor="w")

        columnas = ("producto", "cantidad", "subtotal")
        self.tabla_pedido = ttk.Treeview(marco, columns=columnas, show="headings", height=10)
        for col, txt in zip(columnas, ("Producto", "Cantidad", "Subtotal")):
            self.tabla_pedido.heading(col, text=txt)
            self.tabla_pedido.column(col, width=140)
        self.tabla_pedido.pack(fill="both", expand=True, pady=(6, 6))

        self.etiqueta_total = ttk.Label(marco, text="Total: $0", font=("Segoe UI", 11, "bold"))
        self.etiqueta_total.pack(anchor="e")

        fila_pago = ttk.Frame(marco)
        fila_pago.pack(fill="x", pady=(8, 4))
        ttk.Label(fila_pago, text="Método de pago:").pack(side="left")
        self.var_metodo = tk.StringVar(value=METODOS_PAGO[0])
        ttk.Combobox(fila_pago, textvariable=self.var_metodo, values=METODOS_PAGO,
                     state="readonly", width=14).pack(side="left", padx=6)

        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=(6, 0))
        ttk.Button(botones, text="Confirmar pedido", command=self.confirmar_pedido).pack(side="left", padx=4)
        ttk.Button(botones, text="Generar factura", command=self.generar_factura).pack(side="left", padx=4)
        ttk.Button(botones, text="Nuevo pedido", command=self.nuevo_pedido).pack(side="left", padx=4)

    def refrescar_inventario(self):
        self.tabla_inventario.delete(*self.tabla_inventario.get_children())
        for p in Producto.listar_todos():
            self.tabla_inventario.insert("", "end", iid=p.codigo,
                                          values=(p.codigo, p.nombre, f"{p.precio:,.0f}",
                                                  p.cantidad_disponible))

    def _refrescar_detalle_pedido(self):
        self.tabla_pedido.delete(*self.tabla_pedido.get_children())
        for producto, cantidad in self.pedido_actual.detalle:
            subtotal = producto.precio * cantidad
            self.tabla_pedido.insert("", "end",
                                      values=(producto.nombre, cantidad, f"{subtotal:,.0f}"))
        total = self.pedido_actual.calcular_total()
        self.etiqueta_total.config(text=f"Total: ${total:,.0f}")

    def agregar_al_pedido(self):
        seleccion = self.tabla_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto del inventario.")
            return
        if self.pedido_actual.estado != "pendiente":
            messagebox.showwarning("Pedido cerrado", "Este pedido ya fue confirmado. Crea uno nuevo.")
            return
        try:
            cantidad = int(self.var_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Cantidad inválida", "La cantidad debe ser un entero mayor que 0.")
            return

        codigo = int(seleccion[0])
        producto = Producto.consultar_por_codigo(codigo)
        self.pedido_actual.agregar_producto(producto, cantidad)
        self._refrescar_detalle_pedido()

    def confirmar_pedido(self):
        ok, mensaje = self.pedido_actual.confirmar(self.var_metodo.get())
        if ok:
            messagebox.showinfo("Pedido confirmado", mensaje)
            self.refrescar_inventario()
        else:
            messagebox.showerror("No se pudo confirmar", mensaje)

    def generar_factura(self):
        factura = self.pedido_actual.generar_factura()
        if factura is None:
            messagebox.showwarning("Falta confirmar", "Confirma el pedido antes de generar la factura.")
            return
        messagebox.showinfo(f"Factura pedido #{factura.codigo_pedido}", factura.texto())

    def nuevo_pedido(self):
        self.pedido_actual = Pedido()
        self.etiqueta_codigo.config(text=f"Pedido #{self.pedido_actual.codigo}")
        self._refrescar_detalle_pedido()
        self.refrescar_inventario()


class AplicacionMaxiCream(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Maxi Cream")
        self.geometry("900x560")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.pestaña_productos = PestañaProductos(notebook)
        self.pestaña_pedidos = PestañaPedidos(notebook)

        notebook.add(self.pestaña_productos, text="Productos")
        notebook.add(self.pestaña_pedidos, text="Pedidos y facturación")


if __name__ == "__main__":
    Producto.crear_tabla()
    app = AplicacionMaxiCream()
    app.mainloop()
