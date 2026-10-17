import getpass
import random
import time

import requests


URL = "http://library.demo.local/api/v1/books"

TEMAS = ["Redes", "Python", "Seguridad", "Automatización", "Internet"]
TIPOS = ["Manual", "Guía", "Introducción", "Fundamentos", "Prácticas"]
NOMBRES = ["Ana", "Luis", "Camila", "Pedro", "Sofía", "Martín"]
APELLIDOS = ["Rojas", "Pérez", "Muñoz", "Soto", "Vega", "Díaz"]


def obtener_libros():
    """Obtiene todas las páginas del catálogo y reintenta si la API limita las consultas."""
    todos = []
    pagina = 0

    while True:
        for intento in range(10):
            respuesta = requests.get(
                URL,
                params={"includeISBN": "true", "page": pagina},
                timeout=10,
            )

            if respuesta.status_code != 429:
                break

            print(
                f"Límite temporal en la página {pagina}; "
                "reintentando en 15 segundos..."
            )
            time.sleep(15)
        else:
            raise SystemExit(
                f"La API sigue limitando la página {pagina}. "
                "Inténtalo más tarde."
            )

        respuesta.raise_for_status()
        lote = respuesta.json()

        if not lote:
            break

        todos.extend(lote)

        if len(lote) < 10:
            break

        pagina += 1
        time.sleep(5)

    return todos


libros = obtener_libros()

generados = [
    libro
    for libro in libros
    if libro.get("title", "").startswith("Libro generado ")
]

ids = {libro["id"] for libro in libros}
isbns = {libro.get("isbn") for libro in libros}
faltan = max(0, 50 - len(generados))

print(f"Libros generados anteriormente: {len(generados)}")
print(f"Faltan por agregar: {faltan}")

if faltan > 0:
    token = getpass.getpass("Pega el token de la biblioteca: ").strip()
    if not token:
        raise SystemExit("Falta el token.")

    for numero in range(len(generados) + 1, 51):
        nuevo_id = max(ids) + 1

        while nuevo_id in ids:
            nuevo_id += 1

        isbn = str(random.randint(10**12, 10**13 - 1))
        while isbn in isbns:
            isbn = str(random.randint(10**12, 10**13 - 1))

        libro = {
            "id": nuevo_id,
            "title": (
                f"Libro generado {numero:02d}: "
                f"{random.choice(TIPOS)} de {random.choice(TEMAS)}"
            ),
            "author": (
                f"{random.choice(NOMBRES)} "
                f"{random.choice(APELLIDOS)}"
            ),
            "isbn": isbn,
        }

        respuesta = requests.post(
            URL,
            headers={"X-API-KEY": token},
            json=libro,
            timeout=10,
        )

        if respuesta.status_code not in (200, 201):
            print(f"Error al crear el libro {numero}:")
            print(respuesta.status_code, respuesta.text)
            break

        ids.add(nuevo_id)
        isbns.add(isbn)
        print(f"Creado {numero}/50: ID {nuevo_id} - {libro['title']}")


print("\nCATÁLOGO COMPLETO")
libros = obtener_libros()

for libro in libros:
    print(
        f"ID: {libro['id']} | "
        f"Título: {libro['title']} | "
        f"Autor: {libro['author']} | "
        f"ISBN: {libro.get('isbn', 'sin ISBN')}"
    )

total_generados = sum(
    libro.get("title", "").startswith("Libro generado ")
    for libro in libros
)

print(f"\nLibros generados: {total_generados}/50")
print(f"Total de libros en el catálogo: {len(libros)}")
