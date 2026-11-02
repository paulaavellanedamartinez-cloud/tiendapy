"""Menú principal y flujo general de TiendaPy.

Ejecutar desde la carpeta tiendapy/:  python src/main.py
"""

import inventario
import persistencia
import reportes
import ventas
from validaciones import ReglaNegocioError, pedir_opcion, pedir_fecha

MENU_PRINCIPAL = """
===== TIENDAPY - Tienda Don Aurelio =====
1. Gestión de inventario
2. Registrar venta
3. Alertas de stock
4. Cierre del día
5. Guardar inventario
0. Salir
"""

MENU_INVENTARIO = """
--- Gestión de inventario ---
1. Registrar producto
2. Consultar por código
3. Consultar por categoría
4. Listar todos
5. Modificar precio/stock
6. Eliminar producto
0. Volver
"""


def menu_inventario(inv: dict) -> None:
    acciones = {
        "1": inventario.registrar_producto,
        "2": inventario.consultar_por_codigo,
        "3": inventario.consultar_por_categoria,
        "4": inventario.listar_todos,
        "5": inventario.modificar_producto,
        "6": inventario.borrar_producto,
    }
    while True:
        print(MENU_INVENTARIO)
        opcion = pedir_opcion("Opción: ", ["0", "1", "2", "3", "4", "5", "6"])
        if opcion == "0":
            return
        try:
            acciones[opcion](inv)
        except ReglaNegocioError as error:  # CR-06
            print(f"Error: {error}")


def guardar(inv: dict) -> None:
    persistencia.guardar_inventario(inv)
    print("Inventario guardado.")


def menu_principal(inv: dict, hoy: str) -> None:
    while True:
        print(MENU_PRINCIPAL)
        opcion = pedir_opcion("Opción: ", ["0", "1", "2", "3", "4", "5"])
        try:
            if opcion == "1":
                menu_inventario(inv)
            elif opcion == "2":
                if ventas.flujo_venta(inv, hoy) is not None:
                    guardar(inv)  # el stock descontado no se pierde
            elif opcion == "3":
                reportes.mostrar_alertas(inv)
            elif opcion == "4":
                fecha = pedir_fecha(
                    f"Fecha del cierre AAAA-MM-DD (Enter = {hoy}): ", hoy)
                reportes.mostrar_cierre(inv, persistencia.cargar_ventas(), fecha)
            elif opcion == "5":
                guardar(inv)
            else:
                return
        except ReglaNegocioError as error:  # CR-06
            print(f"Error: {error}")


def main() -> None:
    inv = persistencia.cargar_inventario()
    print(f"Inventario cargado: {len(inv)} productos.")
    hoy = pedir_fecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")
    try:
        menu_principal(inv, hoy)
    except (KeyboardInterrupt, EOFError):
        print("\nEntrada interrumpida.")
    finally:
        guardar(inv)
        print("¡Hasta pronto!")


if __name__ == "__main__":
    main()
