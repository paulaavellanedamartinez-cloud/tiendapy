# TiendaPy

Aplicación de consola en Python para controlar el inventario y las ventas de
una tienda de barrio (caso de estudio: tienda "Don Aurelio", Kennedy, Bogotá).
Proyecto final del curso **Python 0 a 100 – ACM**.

## ¿Qué hace?

|Módulo|Descripción|
|-|-|
|M1 Inventario|Registrar, consultar (por código o categoría), modificar precio/stock y eliminar productos|
|M2 Ventas|Carrito con varios productos, descuento automático, pago, cambio y descuento de stock|
|M3 Alertas|Productos con stock ≤ mínimo, agrupados por proveedor; marca los agotados|
|M4 Reportes|Cierre del día: total, # ventas, ticket promedio, más vendido, sin ventas, categorías con movimiento|
|M5 Persistencia|Inventario en `data/inventario.txt`, historial en `data/ventas.txt`|
|M6 Menú|Menú de consola que se repite hasta elegir "Salir"|

### Reglas de negocio

* No se vende más que el stock disponible.
* Precios, stock y cantidades deben ser mayores que cero.
* Subtotal ≥ $50.000 → 5 % de descuento; ≥ $100.000 → 10 %.
* El pago no puede ser menor al total.
* Los códigos de producto son únicos.
* Stock en cero aparece como **AGOTADO** en las alertas.

## Instalación y ejecución

```bash
git clone <url-del-repositorio>
cd tiendapy

# 1. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\\Scripts\\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar (SIEMPRE desde la carpeta tiendapy/, las rutas son relativas)
python src/main.py
```

Al iniciar, el programa pide la **fecha de hoy** (`AAAA-MM-DD`); se usa para
registrar las ventas y para el cierre del día.

## Pruebas

```bash
python -m unittest discover -s src -v
```

## Formato de los archivos

`data/inventario.txt` (un producto por línea, separado por `|`):

```
codigo|nombre|categoria|precio|stock|stock\_minimo|proveedor
LAC001|Leche entera 1L|Lacteos|4200.0|35|10|Alqueria
```

`data/ventas.txt` (una venta por línea):

```
fecha|total|codigo:cantidad;codigo:cantidad
2026-11-20|18400.0|LAC001:2;BEB003:1
```

## Estructura

```
tiendapy/
├── README.md
├── requirements.txt
├── data/
│   ├── inventario.txt
│   └── ventas.txt
└── src/
    ├── main.py            # menú principal y flujo general
    ├── inventario.py      # CRUD de productos
    ├── ventas.py          # carrito, descuentos y cambio
    ├── reportes.py        # alertas y cierre del día
    ├── persistencia.py    # lectura y escritura de archivos
    ├── validaciones.py    # captura segura de datos
    ├── utilidades.py      # formato de moneda y tablas
    └── test\_tiendapy.py   # pruebas unitarias (unittest)
```

## Decisiones de diseño

* **Sin clases para el modelo de datos:** cada producto es un diccionario y el
inventario es un diccionario `{codigo: producto}`, lo que da búsqueda por
código en O(1) y garantiza códigos únicos de forma natural. El carrito es
`{codigo: cantidad}`. La única clase es `ReglaNegocioError(Exception)`, una
excepción propia.
* **Lógica desacoplada de la interfaz:** funciones como `agregar\_al\_carrito`,
`calcular\_totales` o `crear\_producto` no usan `input()` ni `print()`; las
funciones interactivas solo piden datos y las llaman.
* **Errores de negocio con `raise`:** se lanza `ReglaNegocioError` y se captura
en el menú principal (o localmente cuando hay que reintentar, como el pago).
* **Venta atómica:** `confirmar\_venta` verifica el stock de todo el carrito
antes de descontar nada; si algo falla, el inventario no cambia.
* **Persistencia segura:** `with` + `pathlib.Path` en todos los accesos; se
guarda tras cada venta y al salir (bloque `finally`, incluso con Ctrl+C); las
líneas corruptas se omiten con advertencia.
* **Pruebas:** `unittest` con directorios temporales (`tempfile`) para no
tocar los datos reales.
* **Librería externa:** `tabulate` para mostrar tablas legibles en consola.

## Equipo

* *Maria Paula Avellaneda Martinez*

