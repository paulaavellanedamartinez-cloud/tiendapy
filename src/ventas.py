"""Carrito, descuentos, pago y cambio (M2)."""

from inventario import obtener_producto
from persistencia import registrar_venta
from utilidades import formato_cop, mostrar_tabla
from validaciones import (
    ReglaNegocioError, pedir_entero_positivo, pedir_decimal_positivo,
    confirmar,
)

UMBRAL_DESCUENTO_5 = 50_000
UMBRAL_DESCUENTO_10 = 100_000


# ---------- Lógica (sin input ni print: desacoplada de la interfaz) ----------

def calcular_porcentaje_descuento(subtotal: float) -> float:
    """5 % desde $50.000 y 10 % desde $100.000."""
    if subtotal >= UMBRAL_DESCUENTO_10:
        return 0.10
    elif subtotal >= UMBRAL_DESCUENTO_5:
        return 0.05
    return 0.0


def agregar_al_carrito(inv: dict, carrito: dict, codigo: str,
                       cantidad: int) -> None:
    """Agrega 'cantidad' al carrito sin superar el stock disponible."""
    producto = obtener_producto(inv, codigo)
    if cantidad <= 0:
        raise ReglaNegocioError("La cantidad debe ser mayor que cero.")
    ya_en_carrito = carrito.get(codigo, 0)
    if ya_en_carrito + cantidad > producto["stock"]:
        raise ReglaNegocioError(
            f"Stock insuficiente de '{producto['nombre']}': "
            f"hay {producto['stock']} y el carrito ya tiene {ya_en_carrito}."
        )
    carrito[codigo] = ya_en_carrito + cantidad


def calcular_totales(inv: dict, carrito: dict) -> tuple[float, float, float]:
    """Devuelve (subtotal, descuento, total)."""
    subtotal = 0.0
    for codigo, cantidad in carrito.items():
        subtotal += inv[codigo]["precio"] * cantidad
    descuento = round(subtotal * calcular_porcentaje_descuento(subtotal), 2)
    return subtotal, descuento, round(subtotal - descuento, 2)


def calcular_cambio(total: float, pago: float) -> float:
    if pago < total:
        raise ReglaNegocioError(
            f"Pago insuficiente: faltan {formato_cop(total - pago)}."
        )
    return pago - total


def confirmar_venta(inv: dict, carrito: dict) -> None:
    """Descuenta el stock. Verifica TODO primero: si algo falla, el
    inventario queda intacto (CF-09)."""
    for codigo, cantidad in carrito.items():
        producto = obtener_producto(inv, codigo)
        if cantidad > producto["stock"]:
            raise ReglaNegocioError(
                f"Stock insuficiente de '{producto['nombre']}'."
            )
    for codigo, cantidad in carrito.items():
        inv[codigo]["stock"] -= cantidad


# ---------- Presentación ----------

def mostrar_detalle(inv: dict, carrito: dict) -> None:
    filas = []
    for codigo, cantidad in carrito.items():
        precio = inv[codigo]["precio"]
        filas.append([inv[codigo]["nombre"], cantidad, formato_cop(precio),
                      formato_cop(precio * cantidad)])
    mostrar_tabla(filas, ["Producto", "Cantidad", "Precio unit.", "Valor"])


# ---------- Flujo interactivo ----------

def flujo_venta(inv: dict, fecha: str) -> float | None:
    """Construye una venta. Devuelve el total, o None si se canceló."""
    carrito = {}
    print("\n--- Nueva venta ---")
    print("Escriba 'fin' para terminar o 'cancelar' para abortar.")

    while True:
        codigo = input("Código del producto: ").strip().upper()
        if codigo == "FIN":
            break
        if codigo == "CANCELAR":
            print("Venta cancelada.")
            return None
        try:
            producto = obtener_producto(inv, codigo)
            print(f"  {producto['nombre']} - {formato_cop(producto['precio'])} "
                  f"- disponibles: {producto['stock']}")
            cantidad = pedir_entero_positivo("  Cantidad: ")
            agregar_al_carrito(inv, carrito, codigo, cantidad)
        except ReglaNegocioError as error:
            print(f"Error: {error}")
        else:
            print("  Agregado al carrito.")

    if not carrito:
        print("El carrito está vacío; no se registró ninguna venta.")
        return None

    print("\nDetalle de la venta:")
    mostrar_detalle(inv, carrito)
    subtotal, descuento, total = calcular_totales(inv, carrito)
    print(f"Subtotal:  {formato_cop(subtotal)}")
    print(f"Descuento: {formato_cop(descuento)}")
    print(f"TOTAL:     {formato_cop(total)}")

    while True:  # pago con reintentos (CF-08)
        pago = pedir_decimal_positivo("Pago recibido: ")
        try:
            cambio = calcular_cambio(total, pago)
            break
        except ReglaNegocioError as error:
            print(f"Error: {error}")
            if not confirmar("¿Desea reintentar el pago?"):
                print("Venta cancelada.")
                return None

    if not confirmar("¿Confirmar la venta?"):
        print("Venta cancelada.")
        return None

    confirmar_venta(inv, carrito)  # si falla, sube al menú principal
    registrar_venta(fecha, total, carrito)
    print(f"Venta registrada. Cambio a devolver: {formato_cop(cambio)}")
    return total
