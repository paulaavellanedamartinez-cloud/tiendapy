"""Alertas de stock y cierre del día (M3, M4)."""

from utilidades import formato_cop, mostrar_tabla


def productos_en_alerta(inv: dict) -> dict:
    """Agrupa por proveedor los productos con stock <= stock mínimo."""
    por_proveedor = {}
    for producto in inv.values():
        if producto["stock"] <= producto["stock_minimo"]:
            proveedor = producto["proveedor"]
            if proveedor not in por_proveedor:
                por_proveedor[proveedor] = []
            por_proveedor[proveedor].append(producto)
    return por_proveedor


def mostrar_alertas(inv: dict) -> None:
    print("\n--- Alertas de stock ---")
    por_proveedor = productos_en_alerta(inv)
    if not por_proveedor:
        print("Todos los productos están por encima de su stock mínimo.")
        return
    for proveedor in sorted(por_proveedor):
        print(f"\nProveedor: {proveedor}")
        filas = []
        for p in por_proveedor[proveedor]:
            estado = "AGOTADO" if p["stock"] == 0 else "Stock bajo"
            filas.append([p["codigo"], p["nombre"], p["stock"],
                          p["stock_minimo"], estado])
        mostrar_tabla(filas, ["Código", "Producto", "Stock", "Mínimo", "Estado"])


def calcular_cierre(inv: dict, ventas: list, fecha: str) -> dict:
    """Calcula las métricas del día y las devuelve en un diccionario."""
    total_vendido = 0.0
    cantidad_ventas = 0
    unidades = {}  # codigo -> unidades vendidas ese día

    for venta in ventas:
        if venta["fecha"] != fecha:
            continue
        cantidad_ventas += 1
        total_vendido += venta["total"]
        for codigo, cantidad in venta["items"].items():
            unidades[codigo] = unidades.get(codigo, 0) + cantidad

    ticket = total_vendido / cantidad_ventas if cantidad_ventas > 0 else 0.0

    mas_vendido = None
    mayor = 0
    for codigo, cantidad in unidades.items():
        if cantidad > mayor:
            mayor = cantidad
            nombre = inv[codigo]["nombre"] if codigo in inv else codigo
            mas_vendido = (nombre, cantidad)

    sin_ventas = []
    for codigo, producto in inv.items():
        if codigo not in unidades:
            sin_ventas.append(producto["nombre"])

    categorias = set()
    for codigo in unidades:
        if codigo in inv:
            categorias.add(inv[codigo]["categoria"])

    return {
        "total": total_vendido, "ventas": cantidad_ventas, "ticket": ticket,
        "mas_vendido": mas_vendido, "sin_ventas": sin_ventas,
        "categorias": sorted(categorias),
    }


def mostrar_cierre(inv: dict, ventas: list, fecha: str) -> None:
    cierre = calcular_cierre(inv, ventas, fecha)
    print(f"\n--- Cierre del día {fecha} ---")
    if cierre["mas_vendido"] is not None:
        nombre, cantidad = cierre["mas_vendido"]
        top = f"{nombre} ({cantidad} uds)"
    else:
        top = "Sin ventas"
    categorias = ""
    for categoria in cierre["categorias"]:
        if categorias != "":
            categorias += ", "
        categorias += categoria
    if categorias == "":
        categorias = "Ninguna"
    mostrar_tabla([
        ["Total vendido", formato_cop(cierre["total"])],
        ["Número de ventas", cierre["ventas"]],
        ["Ticket promedio", formato_cop(cierre["ticket"])],
        ["Producto más vendido", top],
        ["Categorías con movimiento", categorias],
    ], ["Indicador", "Valor"])

    print("\nProductos sin ventas:")
    if cierre["sin_ventas"]:
        for nombre in cierre["sin_ventas"]:
            print(f"  - {nombre}")
    else:
        print("  (todos los productos tuvieron ventas)")
