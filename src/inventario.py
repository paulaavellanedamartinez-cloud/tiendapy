"""CRUD de productos (M1). Las reglas de negocio se señalan con raise."""

from utilidades import formato_cop, mostrar_tabla
from validaciones import (
    ReglaNegocioError, pedir_texto, pedir_codigo, pedir_categoria,
    pedir_decimal_positivo, pedir_entero_positivo, pedir_entero_no_negativo,
    confirmar,
)

ENCABEZADOS = ["Código", "Nombre", "Categoría", "Precio", "Stock",
               "Mínimo", "Proveedor"]


# ---------- Lógica ----------

def obtener_producto(inv: dict, codigo: str) -> dict:
    if codigo not in inv:
        raise ReglaNegocioError(f"El producto '{codigo}' no existe.")
    return inv[codigo]


def crear_producto(inv: dict, codigo: str, nombre: str, categoria: str,
                   precio: float, stock: int, stock_minimo: int,
                   proveedor: str) -> None:
    if codigo in inv:
        raise ReglaNegocioError(f"El código '{codigo}' ya está registrado.")
    if precio <= 0 or stock <= 0:
        raise ReglaNegocioError("El precio y el stock deben ser mayores que cero.")
    if stock_minimo < 0:
        raise ReglaNegocioError("El stock mínimo no puede ser negativo.")
    inv[codigo] = {
        "codigo": codigo, "nombre": nombre, "categoria": categoria,
        "precio": float(precio), "stock": stock,
        "stock_minimo": stock_minimo, "proveedor": proveedor,
    }


def modificar_precio(inv: dict, codigo: str, nuevo_precio: float) -> None:
    producto = obtener_producto(inv, codigo)
    if nuevo_precio <= 0:
        raise ReglaNegocioError("El precio debe ser mayor que cero.")
    producto["precio"] = float(nuevo_precio)


def modificar_stock(inv: dict, codigo: str, nuevo_stock: int) -> None:
    producto = obtener_producto(inv, codigo)
    if nuevo_stock <= 0:
        raise ReglaNegocioError("El stock debe ser mayor que cero.")
    producto["stock"] = nuevo_stock


def eliminar_producto(inv: dict, codigo: str) -> dict:
    obtener_producto(inv, codigo)
    return inv.pop(codigo)


def buscar_por_categoria(inv: dict, categoria: str) -> list:
    return [p for p in inv.values() if p["categoria"] == categoria]


# ---------- Presentación ----------

def mostrar_productos(productos: list) -> None:
    filas = [[p["codigo"], p["nombre"], p["categoria"],
              formato_cop(p["precio"]), p["stock"], p["stock_minimo"],
              p["proveedor"]] for p in productos]
    mostrar_tabla(filas, ENCABEZADOS)


# ---------- Flujos interactivos (los errores suben al menú principal) ----------

def registrar_producto(inv: dict) -> None:
    print("\n--- Registrar producto ---")
    codigo = pedir_codigo("Código: ")
    if codigo in inv:  # falla temprano, antes de pedir el resto de datos
        raise ReglaNegocioError(f"El código '{codigo}' ya está registrado.")
    nombre = pedir_texto("Nombre: ")
    categoria = pedir_categoria()
    precio = pedir_decimal_positivo("Precio de venta (COP): ")
    stock = pedir_entero_positivo("Stock inicial: ")
    stock_minimo = pedir_entero_no_negativo("Stock mínimo: ")
    proveedor = pedir_texto("Proveedor: ")
    crear_producto(inv, codigo, nombre, categoria, precio, stock,
                   stock_minimo, proveedor)
    print("Producto registrado correctamente.")


def consultar_por_codigo(inv: dict) -> None:
    codigo = pedir_codigo("Código a consultar: ")
    mostrar_productos([obtener_producto(inv, codigo)])


def consultar_por_categoria(inv: dict) -> None:
    categoria = pedir_categoria()
    productos = buscar_por_categoria(inv, categoria)
    if not productos:
        print(f"No hay productos en la categoría {categoria}.")
    else:
        mostrar_productos(productos)


def listar_todos(inv: dict) -> None:
    if not inv:
        print("El inventario está vacío.")
    else:
        mostrar_productos(list(inv.values()))


def modificar_producto(inv: dict) -> None:
    codigo = pedir_codigo("Código del producto a modificar: ")
    producto = obtener_producto(inv, codigo)
    mostrar_productos([producto])
    print("1. Modificar precio\n2. Modificar stock")
    opcion = input("Opción: ").strip()
    if opcion == "1":
        modificar_precio(inv, codigo, pedir_decimal_positivo("Nuevo precio: "))
        print("Precio actualizado.")
    elif opcion == "2":
        modificar_stock(inv, codigo, pedir_entero_positivo("Nuevo stock: "))
        print("Stock actualizado.")
    else:
        print("Opción no válida.")


def borrar_producto(inv: dict) -> None:
    codigo = pedir_codigo("Código del producto a eliminar: ")
    mostrar_productos([obtener_producto(inv, codigo)])
    if confirmar("¿Seguro que desea eliminarlo?"):
        eliminar_producto(inv, codigo)
        print("Producto eliminado.")
    else:
        print("Operación cancelada.")
