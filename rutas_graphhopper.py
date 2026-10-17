import getpass
import os

import requests


GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
ROUTE_URL = "https://graphhopper.com/api/1/route"


class SalirDelPrograma(Exception):
    pass


def pedir_dato(mensaje):
    valor = input(mensaje).strip()
    if valor.lower() in ("s", "salir"):
        raise SalirDelPrograma
    return valor


def consultar_api(sesion, url, parametros):
    try:
        respuesta = sesion.get(url, params=parametros, timeout=20)
    except requests.RequestException:
        raise ValueError("No se pudo conectar con GraphHopper.")

    if respuesta.status_code != 200:
        raise ValueError(
            f"GraphHopper respondió con HTTP {respuesta.status_code}. "
            "Comprueba la clave, las ubicaciones y el medio de transporte."
        )

    try:
        return respuesta.json()
    except ValueError:
        raise ValueError("GraphHopper devolvió una respuesta no válida.")


def geocodificar(sesion, lugar, clave):
    datos = consultar_api(
        sesion,
        GEOCODE_URL,
        {
            "q": lugar,
            "limit": 1,
            "locale": "es",
            "key": clave,
        },
    )

    resultados = datos.get("hits", [])
    if not resultados:
        raise ValueError(f"No se encontró la ubicación: {lugar}")

    punto = resultados[0]["point"]
    return f"{punto['lat']},{punto['lng']}"


def elegir_transporte():
    print("\nMedios de transporte:")
    print("1. Automóvil")
    print("2. Bicicleta")
    print("3. A pie")

    opciones = {"1": "car", "2": "bike", "3": "foot"}

    while True:
        opcion = pedir_dato("Elige una opción (1, 2 o 3): ")
        if opcion in opciones:
            return opciones[opcion]
        print("Opción no válida. Escribe 1, 2 o 3.")


def mostrar_ruta(sesion, origen, destino, transporte, clave):
    punto_origen = geocodificar(sesion, origen, clave)
    punto_destino = geocodificar(sesion, destino, clave)

    datos = consultar_api(
        sesion,
        ROUTE_URL,
        [
            ("key", clave),
            ("point", punto_origen),
            ("point", punto_destino),
            ("profile", transporte),
            ("locale", "es"),
            ("instructions", "true"),
        ],
    )

    rutas = datos.get("paths", [])
    if not rutas:
        raise ValueError("No se encontró una ruta entre esas ubicaciones.")

    ruta = rutas[0]
    distancia_km = ruta["distance"] / 1000
    duracion_min = ruta["time"] / 60000

    print(f"\nRuta desde {origen} hasta {destino}")
    print(f"Distancia total: {distancia_km:.2f} km")
    print(f"Duración estimada: {duracion_min:.2f} minutos")
    print("\nIndicaciones paso a paso:")

    for numero, indicacion in enumerate(ruta.get("instructions", []), start=1):
        texto = indicacion.get("text", "Continúa")
        distancia_paso_km = indicacion.get("distance", 0) / 1000
        print(f"{numero}. {texto} ({distancia_paso_km:.2f} km)")


def main():
    print("CONSULTA DE RUTAS CON GRAPHHOPPER")
    print("Puedes escribir 's' o 'salir' en cualquier pregunta para terminar.")

    clave = os.environ.get("GRAPHOPPER_API_KEY", "").strip()
    if not clave:
        clave = getpass.getpass("Pega tu clave de GraphHopper: ").strip()

    if not clave:
        print("No se ingresó una clave de GraphHopper.")
        return

    with requests.Session() as sesion:
        while True:
            try:
                origen = pedir_dato("\nLugar de origen: ")
                if not origen:
                    print("Debes escribir un lugar de origen.")
                    continue

                destino = pedir_dato("Lugar de destino: ")
                if not destino:
                    print("Debes escribir un lugar de destino.")
                    continue

                transporte = elegir_transporte()
                mostrar_ruta(sesion, origen, destino, transporte, clave)

            except SalirDelPrograma:
                print("\nPrograma finalizado.")
                break
            except ValueError as error:
                print(f"\nError: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")