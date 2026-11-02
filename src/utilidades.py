"""Funciones de presentación: formato de moneda y tablas en consola."""

from tabulate import tabulate


def formato_cop(valor: float) -> str:
    """Devuelve un número como moneda: 4200.0 -> '$4,200'."""
    return f"${valor:,.0f}"


def mostrar_tabla(filas: list, encabezados: list) -> None:
    """Imprime una tabla usando la librería tabulate."""
    print(tabulate(filas, headers=encabezados, tablefmt="grid"))
