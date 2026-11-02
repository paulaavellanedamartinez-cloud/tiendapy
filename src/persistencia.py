"""Lectura y escritura de archivos de texto plano (M5, CR-03 a CR-05).

Las rutas son relativas: el programa se ejecuta desde la carpeta tiendapy/.
"""

from pathlib import Path

from validaciones import es_fecha_valida, normalizar_categoria

RUTA_INVENTARIO = Path("data") / "inventario.txt"
RUTA_VENTAS = Path("data") / "ventas.txt"


# ---------- Inventario ----------

def _parsear_producto(linea: str) -> dict:
    """Convierte 'a|b|c|...' en un diccionario de producto.
    Lanza ValueError con un mensaje claro si la línea es inválida."""
    partes = linea.split("|")
    if len(partes) != 7:
        raise ValueError(f"se esperaban 7 campos y hay {len(partes)}")

    codigo = partes[0].strip()
    nombre = partes[1].strip()
    categoria = partes[2].strip()
    proveedor = partes[6].strip()
    if codigo == "" or nombre == "" or proveedor == "":
        raise ValueError("hay campos de texto vacíos")

    categoria = normalizar_categoria(categoria)

    try:
        precio = float(partes[3])
        stock = int(partes[4])
        minimo = int(partes[5])
    except ValueError:
        raise ValueError("precio, stock o stock mínimo no son números válidos")

    if precio <= 0 or stock < 0 or minimo < 0:
        raise ValueError("precio o cantidades fuera de rango")

    return {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
        "stock_minimo": minimo,
        "proveedor": proveedor,
    }


def cargar_inventario(ruta: Path = RUTA_INVENTARIO) -> dict:
    """Carga el inventario. Omite líneas corruptas con advertencia (CR-04)
    y arranca vacío si el archivo no existe (CR-03)."""
    inventario = {}
    try:
        with ruta.open("r", encoding="utf-8", errors="replace") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if linea == "":
                    continue
                try:
                    producto = _parsear_producto(linea)
                except ValueError as error:
                    print(f"Advertencia: línea {numero} omitida ({error}).")
                    continue
                if producto["codigo"] in inventario:
                    print(f"Advertencia: línea {numero} omitida "
                          f"(código repetido '{producto['codigo']}').")
                    continue
                inventario[producto["codigo"]] = producto
    except FileNotFoundError:
        print(f"Aviso: no se encontró '{ruta}'. "
              "Se inicia con un inventario vacío.")
    return inventario


def guardar_inventario(inventario: dict, ruta: Path = RUTA_INVENTARIO) -> None:
    """Escribe todo el inventario, un producto por línea."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as archivo:
        for p in inventario.values():
            archivo.write(
                f"{p['codigo']}|{p['nombre']}|{p['categoria']}|{p['precio']}|"
                f"{p['stock']}|{p['stock_minimo']}|{p['proveedor']}\n"
            )


# ---------- Ventas ----------

def registrar_venta(fecha: str, total: float, carrito: dict,
                    ruta: Path = RUTA_VENTAS) -> None:
    """Agrega una venta al final del historial: fecha|total|cod:cant;cod:cant"""
    detalle = ""
    for codigo, cantidad in carrito.items():
        if detalle != "":
            detalle += ";"
        detalle += f"{codigo}:{cantidad}"

    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha}|{total}|{detalle}\n")


def _parsear_venta(linea: str) -> dict:
    partes = linea.split("|")
    if len(partes) != 3:
        raise ValueError("se esperaban 3 campos")
    fecha = partes[0].strip()
    if not es_fecha_valida(fecha):
        raise ValueError("fecha inválida")
    items = {}
    for par in partes[2].split(";"):
        codigo, cantidad = par.split(":")  # ValueError si no hay 2 partes
        codigo = codigo.strip()
        items[codigo] = items.get(codigo, 0) + int(cantidad)
    return {"fecha": fecha, "total": float(partes[1]), "items": items}


def cargar_ventas(ruta: Path = RUTA_VENTAS) -> list:
    """Devuelve la lista de ventas del historial (omite líneas corruptas)."""
    ventas = []
    try:
        with ruta.open("r", encoding="utf-8", errors="replace") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if linea == "":
                    continue
                try:
                    ventas.append(_parsear_venta(linea))
                except ValueError:
                    print(f"Advertencia: venta en la línea {numero} "
                          "omitida (formato inválido).")
    except FileNotFoundError:
        pass  # aún no hay historial: es normal
    return ventas
