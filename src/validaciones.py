"""Captura segura de datos y reglas de validación (CR-01, CR-02)."""

CATEGORIAS: list[str] = ["Lacteos", "Bebidas", "Aseo", "Abarrotes", "Snacks"]

# Permite leer 'Lácteos' o 'lacteos' del archivo y unificarlo.
ALIAS_CATEGORIAS: dict[str, str] = {
    "lacteos": "Lacteos",
    "lácteos": "Lacteos",
    "bebidas": "Bebidas",
    "aseo": "Aseo",
    "abarrotes": "Abarrotes",
    "snacks": "Snacks",
}

LIMITE_MAXIMO = 1_000_000_000_000  # descarta valores absurdos (también inf y nan)


class ReglaNegocioError(Exception):
    """Se lanza (raise) cuando se viola una regla de negocio."""


# ---------- Captura de datos ----------

def pedir_texto(mensaje: str) -> str:
    """Pide un texto no vacío que no contenga el separador '|'."""
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            print("Error: este campo no puede estar vacío.")
        elif "|" in texto:
            print("Error: el carácter '|' no está permitido.")
        else:
            return texto


def pedir_codigo(mensaje: str) -> str:
    """Pide un código sin espacios ni caracteres reservados, en mayúsculas."""
    while True:
        codigo = pedir_texto(mensaje).upper()
        if " " in codigo or ":" in codigo or ";" in codigo:
            print("Error: el código no puede tener espacios, ':' ni ';'.")
        else:
            return codigo


def pedir_entero_positivo(mensaje: str) -> int:
    """Pide un entero mayor que cero; repite hasta que sea válido."""
    while True:
        try:
            valor = int(input(mensaje).strip())
        except ValueError:
            print("Error: ingrese un número entero válido.")
            continue
        if valor <= 0:
            print("Error: el valor debe ser mayor que cero.")
            continue
        return valor


def pedir_entero_no_negativo(mensaje: str) -> int:
    """Pide un entero mayor o igual a cero (p. ej. stock mínimo)."""
    while True:
        try:
            valor = int(input(mensaje).strip())
        except ValueError:
            print("Error: ingrese un número entero válido.")
            continue
        if valor < 0:
            print("Error: el valor no puede ser negativo.")
            continue
        return valor


def pedir_decimal_positivo(mensaje: str) -> float:
    """Pide un número decimal mayor que cero; repite hasta que sea válido."""
    while True:
        try:
            valor = float(input(mensaje).strip())
        except ValueError:
            print("Error: ingrese un número válido (ej. 4200 o 4200.5).")
            continue
        if not 0 < valor < LIMITE_MAXIMO:
            print("Error: el valor debe ser mayor que cero.")
            continue
        return valor


def pedir_opcion(mensaje: str, validas: list) -> str:
    """Pide una opción que esté dentro de 'validas' (lista de str)."""
    while True:
        opcion = input(mensaje).strip().lower()
        if opcion in validas:
            return opcion
        print("Opción no válida. Intente de nuevo.")


def confirmar(mensaje: str) -> bool:
    """Pregunta sí/no. Devuelve True si responde 's'."""
    return pedir_opcion(mensaje + " (s/n): ", ["s", "n"]) == "s"


def pedir_categoria() -> str:
    """Muestra las categorías numeradas y devuelve la elegida."""
    opciones = []
    for numero, categoria in enumerate(CATEGORIAS, start=1):
        print(f"  {numero}. {categoria}")
        opciones.append(str(numero))
    eleccion = pedir_opcion("Categoría (número): ", opciones)
    return CATEGORIAS[int(eleccion) - 1]


# ---------- Fechas (formato AAAA-MM-DD) ----------

def es_fecha_valida(texto: str) -> bool:
    """Revisa que el texto tenga la forma AAAA-MM-DD con mes y día posibles."""
    partes = texto.split("-")
    if len(partes) != 3:
        return False
    if len(partes[0]) != 4 or len(partes[1]) != 2 or len(partes[2]) != 2:
        return False
    try:
        mes = int(partes[1])
        dia = int(partes[2])
        int(partes[0])
    except ValueError:
        return False
    return 1 <= mes <= 12 and 1 <= dia <= 31


def pedir_fecha(mensaje: str, por_defecto: str | None = None) -> str:
    """Pide una fecha AAAA-MM-DD. Con Enter devuelve 'por_defecto' si existe."""
    while True:
        texto = input(mensaje).strip()
        if texto == "" and por_defecto is not None:
            return por_defecto
        if es_fecha_valida(texto):
            return texto
        print("Error: use el formato AAAA-MM-DD (ej. 2026-11-20).")


# ---------- Normalización ----------

def normalizar_categoria(texto: str) -> str:
    """Convierte 'Lácteos'/'lacteos' en 'Lacteos'. Lanza ValueError si no existe."""
    clave = texto.strip().lower()
    if clave not in ALIAS_CATEGORIAS:
        raise ValueError(f"categoría desconocida '{texto}'")
    return ALIAS_CATEGORIAS[clave]
