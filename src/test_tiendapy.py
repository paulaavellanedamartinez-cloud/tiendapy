"""Pruebas unitarias de TiendaPy.

Ejecutar desde la carpeta tiendapy/:  python -m unittest discover -s src -v
"""

import tempfile
import unittest
from pathlib import Path

import inventario
import persistencia
import reportes
import ventas
from validaciones import ReglaNegocioError, es_fecha_valida


def inventario_base() -> dict:
    return {
        "A": {"codigo": "A", "nombre": "Arroz", "categoria": "Abarrotes",
              "precio": 1000.0, "stock": 5, "stock_minimo": 2,
              "proveedor": "P1"},
        "B": {"codigo": "B", "nombre": "Jugo", "categoria": "Bebidas",
              "precio": 2000.0, "stock": 0, "stock_minimo": 3,
              "proveedor": "P2"},
    }


class TestVentas(unittest.TestCase):
    def test_descuentos_en_los_umbrales(self) -> None:
        self.assertEqual(ventas.calcular_porcentaje_descuento(49_999), 0.0)
        self.assertEqual(ventas.calcular_porcentaje_descuento(50_000), 0.05)
        self.assertEqual(ventas.calcular_porcentaje_descuento(99_999), 0.05)
        self.assertEqual(ventas.calcular_porcentaje_descuento(100_000), 0.10)

    def test_totales_con_descuento(self) -> None:
        inv = inventario_base()
        inv["A"]["precio"] = 20_000.0
        inv["A"]["stock"] = 10
        subtotal, descuento, total = ventas.calcular_totales(inv, {"A": 3})
        self.assertEqual((subtotal, descuento, total), (60_000, 3_000, 57_000))

    def test_no_se_vende_mas_que_el_stock(self) -> None:
        inv = inventario_base()
        with self.assertRaises(ReglaNegocioError):
            ventas.agregar_al_carrito(inv, {}, "A", 6)

    def test_carrito_acumula_y_respeta_stock(self) -> None:
        inv = inventario_base()
        carrito = {}
        ventas.agregar_al_carrito(inv, carrito, "A", 3)
        with self.assertRaises(ReglaNegocioError):
            ventas.agregar_al_carrito(inv, carrito, "A", 3)
        self.assertEqual(carrito, {"A": 3})

    def test_venta_rechazada_no_cambia_inventario(self) -> None:
        inv = inventario_base()
        with self.assertRaises(ReglaNegocioError):
            ventas.confirmar_venta(inv, {"A": 2, "B": 1})
        self.assertEqual(inv["A"]["stock"], 5)

    def test_venta_confirmada_descuenta_stock(self) -> None:
        inv = inventario_base()
        ventas.confirmar_venta(inv, {"A": 2})
        self.assertEqual(inv["A"]["stock"], 3)

    def test_pago_insuficiente_y_cambio(self) -> None:
        with self.assertRaises(ReglaNegocioError):
            ventas.calcular_cambio(1000, 500)
        self.assertEqual(ventas.calcular_cambio(1000, 1500), 500)


class TestInventario(unittest.TestCase):
    def test_codigo_duplicado_rechazado(self) -> None:
        inv = inventario_base()
        with self.assertRaises(ReglaNegocioError):
            inventario.crear_producto(inv, "A", "x", "Aseo", 1.0, 1, 0, "p")

    def test_valores_no_positivos_rechazados(self) -> None:
        inv = inventario_base()
        with self.assertRaises(ReglaNegocioError):
            inventario.crear_producto(inv, "C", "x", "Aseo", -5.0, 1, 0, "p")
        with self.assertRaises(ReglaNegocioError):
            inventario.crear_producto(inv, "C", "x", "Aseo", 5.0, 0, 0, "p")

    def test_producto_inexistente(self) -> None:
        with self.assertRaises(ReglaNegocioError):
            inventario.obtener_producto(inventario_base(), "ZZZ")

    def test_eliminar_producto(self) -> None:
        inv = inventario_base()
        inventario.eliminar_producto(inv, "A")
        self.assertNotIn("A", inv)


class TestPersistencia(unittest.TestCase):
    def setUp(self) -> None:
        self.dir_temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self.dir_temporal.name)

    def tearDown(self) -> None:
        self.dir_temporal.cleanup()

    def test_guardar_y_cargar(self) -> None:
        ruta = self.carpeta / "data" / "inventario.txt"
        inv = inventario_base()
        persistencia.guardar_inventario(inv, ruta)
        self.assertEqual(persistencia.cargar_inventario(ruta), inv)

    def test_archivo_inexistente_devuelve_vacio(self) -> None:
        ruta = self.carpeta / "no_existe.txt"
        self.assertEqual(persistencia.cargar_inventario(ruta), {})

    def test_lineas_corruptas_se_omiten(self) -> None:
        ruta = self.carpeta / "inv.txt"
        ruta.write_text(
            "LAC001|Leche|Lácteos|4200.0|35|10|Alqueria\n"
            "basura sin separadores\n"
            "BEB001|Agua|Bebidas|abc|5|2|Postobon\n"
            "BEB002|Jugo|Bebidas|-5|5|2|Postobon\n"
            "LAC001|Repetido|Lacteos|1.0|1|1|X\n"
            "ASE001|Jabon|Aseo|2800.0|0|8|Norte\n",
            encoding="utf-8",
        )
        inv = persistencia.cargar_inventario(ruta)
        self.assertEqual(list(inv), ["LAC001", "ASE001"])
        self.assertEqual(inv["LAC001"]["categoria"], "Lacteos")

    def test_historial_de_ventas(self) -> None:
        ruta = self.carpeta / "ventas.txt"
        persistencia.registrar_venta("2026-11-20", 18400.0,
                                     {"LAC001": 2, "BEB003": 1}, ruta)
        self.assertEqual(ruta.read_text(encoding="utf-8"),
                         "2026-11-20|18400.0|LAC001:2;BEB003:1\n")
        cargadas = persistencia.cargar_ventas(ruta)
        self.assertEqual(cargadas[0]["items"], {"LAC001": 2, "BEB003": 1})


class TestReportes(unittest.TestCase):
    def test_alertas_agrupadas_por_proveedor(self) -> None:
        alertas = reportes.productos_en_alerta(inventario_base())
        self.assertEqual(list(alertas), ["P2"])  # A (5 > 2) no alerta
        self.assertEqual(alertas["P2"][0]["stock"], 0)  # agotado

    def test_cierre_del_dia(self) -> None:
        inv = inventario_base()
        historial = [
            {"fecha": "2026-11-20", "total": 3000.0, "items": {"A": 3}},
            {"fecha": "2026-11-20", "total": 1000.0, "items": {"A": 1}},
            {"fecha": "2026-11-19", "total": 9999.0, "items": {"B": 5}},
        ]
        cierre = reportes.calcular_cierre(inv, historial, "2026-11-20")
        self.assertEqual(cierre["total"], 4000.0)
        self.assertEqual(cierre["ventas"], 2)
        self.assertEqual(cierre["ticket"], 2000.0)
        self.assertEqual(cierre["mas_vendido"], ("Arroz", 4))
        self.assertEqual(cierre["sin_ventas"], ["Jugo"])
        self.assertEqual(cierre["categorias"], ["Abarrotes"])


class TestFechas(unittest.TestCase):
    def test_fechas(self) -> None:
        self.assertTrue(es_fecha_valida("2026-11-20"))
        self.assertFalse(es_fecha_valida("2026-13-45"))
        self.assertFalse(es_fecha_valida("20-11-2026"))
        self.assertFalse(es_fecha_valida("hola"))


if __name__ == "__main__":
    unittest.main()
