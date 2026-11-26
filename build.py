#!/usr/bin/env python3
"""
Genera las partes de la web que dependen de la lista de obras (data/obras.json).

    python3 build.py

Qué hace:
  1. Reescribe las tarjetas de la galería en index.html (español) e
     index-en.html (inglés), entre las marcas <!-- OBRAS:INICIO --> y
     <!-- OBRAS:FIN -->. El resto de cada página no se toca.
  2. Crea una página para cada obra: obras/<id>.html y obras/<id>-en.html.
  3. Reescribe sitemap.xml con todas las páginas.

Para añadir una obra, marcarla como vendida o cambiar un precio:
editar data/obras.json y volver a ejecutar este programa.
El orden de la lista es el orden en la galería.

Campos de cada obra:
  id          identificador sin espacios ni tildes; es la dirección de su página
  titulo      nombre de la obra
  imagen      nombre del archivo en images/works/
  tecnica     técnica en español   ("Óleo sobre tabla")
  tecnica_en  técnica en inglés    ("Oil on panel")
  medidas     "34 x 24 cm"  (alto x ancho)
  fecha       año y mes, "2025-09"
  precio      en euros, solo el número (270)
  vendida     true / false
  marco       true si incluye marco artesanal
  texto       (opcional) texto sobre la obra en español; párrafos separados por una línea en blanco
  texto_en    (opcional) el mismo texto en inglés
"""

import hashlib
import json
import re
import shutil
import struct
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE = "https://andreacasanya.com/"
EMAIL = "art.andreacasanya@gmail.com"
ARTISTA = "Andrea Casanya"

INICIO = "<!-- OBRAS:INICIO (generado por build.py a partir de data/obras.json: no editar a mano) -->"
FIN = "<!-- OBRAS:FIN -->"

# Páginas fijas de la web (español, inglés), para el mapa del sitio
PAGINAS = [
    ("index.html", "index-en.html"),
    ("sobre-mi.html", "about_me-en.html"),
    ("proceso.html", "process-en.html"),
    ("contacto.html", "contact-en.html"),
    # el aviso legal no va en el mapa: tiene noindex para que Google no muestre NIF y dirección
]

IDIOMAS = {
    "es": {
        "galeria": "index.html",
        "sufijo": "",
        "locale": "es_ES",
        "meses": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                  "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
        "titulo": "Título",
        "tecnica": "Técnica",
        "medidas": "Dimensiones",
        "fecha": "Fecha",
        "precio": "Precio",
        "me_gusta": "Me gusta",
        "vendida": "Adquirido",
        "comprar": "Adquirir obra",
        "envio": "Consultar envío",
        "envio_enlace": "contacto.html#envios",
        "marco": "Marco artesanal incluido",
        "serie": "Serie París 2025",
        "volver": "Volver a las obras",
        "anterior": "Obra anterior",
        "siguiente": "Obra siguiente",
        "asunto": "[Web] Consulta de adquisición — {titulo}",
        "mensaje": "Hola Andrea,\r\n\r\nMe gustaría adquirir la obra \"{titulo}\".\r\n\r\n"
                   "Quedo a la espera de tu respuesta.\r\n\r\nUn saludo,",
        "descripcion": "{titulo}, {tecnica} de Andrea Casanya ({medidas}, {mes} de {año}). "
                       "Serie París 2025. {estado}",
        "disponible": "Obra original disponible.",
        "adquirida": "Obra original, adquirida.",
    },
    "en": {
        "galeria": "index-en.html",
        "sufijo": "-en",
        "locale": "en_GB",
        "meses": ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"],
        "titulo": "Title",
        "tecnica": "Medium",
        "medidas": "Dimensions",
        "fecha": "Date",
        "precio": "Price",
        "me_gusta": "Like",
        "vendida": "Sold",
        "comprar": "Acquire this work",
        "envio": "Shipping inquiries",
        "envio_enlace": "contact-en.html#shipping",
        "marco": "Handcrafted frame included",
        "serie": "Paris Series 2025",
        "volver": "Back to works",
        "anterior": "Previous work",
        "siguiente": "Next work",
        "asunto": "[Web] Purchase inquiry — {titulo}",
        "mensaje": "Hello Andrea,\r\n\r\nI would like to acquire the artwork \"{titulo}\".\r\n\r\n"
                   "Looking forward to your reply.\r\n\r\nBest regards,",
        "descripcion": "{titulo}, {tecnica} by Andrea Casanya ({medidas}, {mes} {año}). "
                       "Paris Series 2025. {estado}",
        "disponible": "Original artwork, available.",
        "adquirida": "Original artwork, sold.",
    },
}

CAMPOS = ["id", "titulo", "imagen", "tecnica", "tecnica_en", "medidas", "fecha", "precio", "vendida", "marco"]


# ---------------------------------------------------------------- utilidades

def medidas_jpeg(ruta):
    """Ancho y alto de una foto JPEG, sin instalar nada."""
    with open(ruta, "rb") as f:
        f.read(2)
        while True:
            marca, tipo, largo = struct.unpack(">BBH", f.read(4))
            if tipo in (0xC0, 0xC1, 0xC2):
                alto, ancho = struct.unpack(">xHH", f.read(5))
                return ancho, alto
            f.read(largo - 2)


def fecha_texto(o, t, mayuscula=True):
    año, mes = o["fecha"].split("-")
    nombre = t["meses"][int(mes) - 1]
    if mayuscula:
        nombre = nombre[0].upper() + nombre[1:]
    return nombre, año


def mailto(o, t):
    asunto = quote(t["asunto"].format(titulo=o["titulo"]))
    mensaje = quote(t["mensaje"].format(titulo=o["titulo"]))
    return f"mailto:{EMAIL}?subject={asunto}&amp;body={mensaje}"


def version(ruta):
    """Código corto que cambia cuando cambia el archivo: así el navegador no usa una copia antigua."""
    return hashlib.md5((ROOT / ruta).read_bytes()).hexdigest()[:8]


def pagina_obra(o, lang):
    return f"obras/{o['id']}{IDIOMAS[lang]['sufijo']}.html"


def sangrar(lineas, sangria):
    return "\n".join((sangria + l) if l else "" for l in lineas)


def cargar_obras():
    obras = json.loads((ROOT / "data" / "obras.json").read_text(encoding="utf-8"))
    errores = []
    ids = set()
    for n, o in enumerate(obras, 1):
        nombre = o.get("titulo", f"obra n.º {n}")
        faltan = [c for c in CAMPOS if c not in o]
        if faltan:
            errores.append(f"«{nombre}»: faltan los campos {', '.join(faltan)}")
            continue
        if not (ROOT / "images" / "works" / o["imagen"]).exists():
            errores.append(f"«{nombre}»: no existe la imagen images/works/{o['imagen']}")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", o["id"]):
            errores.append(f"«{nombre}»: el id «{o['id']}» solo puede tener minúsculas, números y guiones")
        if o["id"] in ids:
            errores.append(f"«{nombre}»: el id «{o['id']}» está repetido")
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", str(o["fecha"])):
            errores.append(f"«{nombre}»: la fecha «{o['fecha']}» debe ser año-mes, por ejemplo 2025-09")
        ids.add(o["id"])
    if errores:
        sys.exit("No se ha generado nada. Hay que corregir data/obras.json:\n  - " + "\n  - ".join(errores))
    return obras


# ---------------------------------------------------------------- galería

def tarjeta(o, t, lang):
    titulo = escape(o["titulo"])
    tecnica = escape(o["tecnica"] if lang == "es" else o["tecnica_en"])
    mes, año = fecha_texto(o, t)
    i = " " * 4
    lineas = [
        f'<article class="work-card" data-fecha="{o["fecha"]}">',
        f'{i}<a href="{pagina_obra(o, lang)}" class="work-image-link">',
        f'{i*2}<img src="images/works/{escape(o["imagen"])}" alt="{titulo}" class="work-image" loading="lazy">',
        f'{i}</a>',
        f'{i}<div class="work-info">',
        f'{i*2}<div class="work-title-row">',
        f'{i*3}<p class="work-title">{t["titulo"]}: <strong>{titulo}</strong></p>',
        f'{i*3}<button class="btn-like" data-work-id="{titulo}" onclick="toggleLike(this)">',
        f'{i*4}<img src="images/ui/corazon-vacio.png" alt="{t["me_gusta"]}" class="heart-img" '
        f'data-empty="images/ui/corazon-vacio.png" data-filled="images/ui/corazon-lleno.png">',
        f'{i*3}</button>',
        f'{i*2}</div>',
        f'{i*2}<p>{t["tecnica"]}: <strong>{tecnica}</strong></p>',
        f'{i*2}<p>{t["medidas"]}: <strong>{escape(o["medidas"])}</strong></p>',
        f'{i*2}<p>{t["fecha"]}: <strong>{mes} {año}</strong></p>',
        f'{i*2}<p>{t["precio"]}: <strong>{o["precio"]} €</strong></p>',
    ]
    if o["vendida"]:
        lineas += [
            f'{i*2}<div class="status-sold">',
            f'{i*3}<span class="red-dot"></span>',
            f'{i*3}<span class="status-text">{t["vendida"]}</span>',
            f'{i*2}</div>',
        ]
    else:
        lineas += [
            f'{i*2}<div class="work-actions">',
            f'{i*3}<a href="{mailto(o, t)}" class="btn-inquire">{t["comprar"]}</a>',
            f'{i*2}</div>',
            f'{i*2}<a href="{t["envio_enlace"]}" class="link-envio">{t["envio"]}</a>',
        ]
        if o["marco"]:
            lineas.append(f'{i*2}<p class="link-envio frame-note">{t["marco"]}</p>')
    lineas += [f'{i}</div>', '</article>']
    return lineas


def generar_galeria(obras, lang):
    t = IDIOMAS[lang]
    ruta = ROOT / t["galeria"]
    html = ruta.read_text(encoding="utf-8")

    patron = re.compile(r"([ \t]*)" + re.escape(INICIO) + r".*?" + re.escape(FIN), re.S)
    m = patron.search(html)
    if not m:
        sys.exit(f"No encuentro las marcas OBRAS:INICIO / OBRAS:FIN en {t['galeria']}")

    bloque = [INICIO, ""]
    for n, o in enumerate(obras, 1):
        nota = f" ({t['vendida']})" if o["vendida"] else ""
        bloque.append(f"<!-- {n}. {escape(o['titulo'])}{nota} -->")
        bloque += tarjeta(o, t, lang)
        bloque.append("")
    bloque.append(FIN)

    html = html[:m.start()] + sangrar(bloque, m.group(1)) + html[m.end():]
    ruta.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- páginas de obra

def subir_un_nivel(fragmento):
    """Las páginas de obra están en obras/: las rutas relativas necesitan ../ delante."""
    def arreglar(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"(https?:|mailto:|#|/|\.\./)", url):
            return m.group(0)
        return f'{attr}="../{url}"'
    return re.sub(r'(href|src)="([^"]*)"', arreglar, fragmento)


def cabecera_y_pie(lang, o):
    """Copia la cabecera y el pie de la galería, para que todas las páginas sean iguales."""
    html = (ROOT / IDIOMAS[lang]["galeria"]).read_text(encoding="utf-8")
    cabecera = re.search(r"<header class=\"navbar\">.*?</header>", html, re.S).group(0)
    pie = re.search(r"<footer>.*?</footer>", html, re.S).group(0)
    galeria = IDIOMAS[lang]["galeria"]
    cabecera = cabecera.replace('href="#obras"', f'href="{galeria}#obras"')
    cabecera = subir_un_nivel(cabecera)
    # el selector de idioma lleva a esta misma obra en el otro idioma
    cabecera = cabecera.replace('href="../index.html" class="lang-btn',
                                f'href="{o["id"]}.html" class="lang-btn')
    cabecera = cabecera.replace('href="../index-en.html" class="lang-btn',
                                f'href="{o["id"]}-en.html" class="lang-btn')
    return cabecera, subir_un_nivel(pie)


def datos_estructurados(o, lang, ancho, alto):
    """Ficha de la obra en el formato que entiende Google (schema.org VisualArtwork)."""
    t = IDIOMAS[lang]
    alto_cm, ancho_cm = [x.strip() for x in o["medidas"].replace("cm", "").split("x")]
    datos = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "name": o["titulo"],
        "image": SITE + "images/works/" + o["imagen"],
        "url": SITE + pagina_obra(o, lang),
        "creator": {"@type": "Person", "name": ARTISTA, "url": SITE},
        "artform": "Painting" if lang == "en" else "Pintura",
        "artMedium": o["tecnica_en"] if lang == "en" else o["tecnica"],
        "height": {"@type": "QuantitativeValue", "value": float(alto_cm), "unitCode": "CMT"},
        "width": {"@type": "QuantitativeValue", "value": float(ancho_cm), "unitCode": "CMT"},
        "dateCreated": o["fecha"],
        "isPartOf": t["serie"],
        "offers": {
            "@type": "Offer",
            "price": o["precio"],
            "priceCurrency": "EUR",
            "availability": "https://schema.org/SoldOut" if o["vendida"] else "https://schema.org/InStock",
            "url": SITE + pagina_obra(o, lang),
        },
    }
    return json.dumps(datos, ensure_ascii=False, indent=2).replace("</", "<\\/")


def generar_pagina_obra(obras, n, lang):
    o = obras[n]
    t = IDIOMAS[lang]
    otro = "en" if lang == "es" else "es"
    titulo = escape(o["titulo"])
    tecnica = o["tecnica"] if lang == "es" else o["tecnica_en"]
    mes, año = fecha_texto(o, t)
    mes_min, _ = fecha_texto(o, t, mayuscula=False)
    ancho, alto = medidas_jpeg(ROOT / "images" / "works" / o["imagen"])

    descripcion = t["descripcion"].format(
        titulo=o["titulo"],
        tecnica=tecnica[0].lower() + tecnica[1:] if lang == "es" else tecnica.lower(),
        medidas=o["medidas"], mes=mes_min, año=año,
        estado=t["adquirida"] if o["vendida"] else t["disponible"],
    )
    descripcion = escape(descripcion)
    titulo_pagina = f"{titulo} — {escape(tecnica)} | Casanya"
    url = SITE + pagina_obra(o, lang)
    url_es, url_en = SITE + pagina_obra(o, "es"), SITE + pagina_obra(o, "en")
    imagen = SITE + "images/works/" + escape(o["imagen"])
    cabecera, pie = cabecera_y_pie(lang, o)

    anterior = obras[(n - 1) % len(obras)]
    siguiente = obras[(n + 1) % len(obras)]

    # texto opcional sobre la obra
    texto = o.get("texto" if lang == "es" else "texto_en", "").strip()
    parrafos = [f'<p class="obra-texto">{escape(p.strip())}</p>' for p in re.split(r"\n\s*\n", texto) if p.strip()]

    if o["vendida"]:
        compra = [
            '<div class="status-sold">',
            '    <span class="red-dot"></span>',
            f'    <span class="status-text">{t["vendida"]}</span>',
            '</div>',
        ]
    else:
        compra = [
            '<div class="work-actions">',
            f'    <a href="{mailto(o, t)}" class="btn-inquire">{t["comprar"]}</a>',
            '</div>',
            f'<a href="../{t["envio_enlace"]}" class="link-envio">{t["envio"]}</a>',
        ]
        if o["marco"]:
            compra.append(f'<p class="link-envio frame-note">{t["marco"]}</p>')

    ficha = [
        f'<p class="obra-serie">{t["serie"]}</p>',
        f'<h1 class="obra-titulo">{titulo}</h1>',
        '<dl class="obra-datos">',
        f'    <div><dt>{t["tecnica"]}</dt><dd>{escape(tecnica)}</dd></div>',
        f'    <div><dt>{t["medidas"]}</dt><dd>{escape(o["medidas"])}</dd></div>',
        f'    <div><dt>{t["fecha"]}</dt><dd>{mes} {año}</dd></div>',
        f'    <div><dt>{t["precio"]}</dt><dd>{o["precio"]} €</dd></div>',
        '</dl>',
    ] + parrafos + compra

    principal = [
        '<main class="page-content obra-page">',
        f'    <a href="../{t["galeria"]}#obras" class="obra-volver">← {t["volver"]}</a>',
        '',
        '    <article class="obra-layout">',
        '        <div class="obra-imagen">',
        f'            <img src="../images/works/{escape(o["imagen"])}" alt="{titulo}" width="{ancho}" height="{alto}">',
        '        </div>',
        '        <div class="work-info obra-ficha">',
        sangrar(ficha, " " * 12),
        '        </div>',
        '    </article>',
        '',
        '    <nav class="obra-nav">',
        f'        <a href="{anterior["id"]}{t["sufijo"]}.html" class="obra-nav-prev">',
        f'            <span class="obra-nav-label">← {t["anterior"]}</span>',
        f'            <span class="obra-nav-titulo">{escape(anterior["titulo"])}</span>',
        '        </a>',
        f'        <a href="{siguiente["id"]}{t["sufijo"]}.html" class="obra-nav-next">',
        f'            <span class="obra-nav-label">{t["siguiente"]} →</span>',
        f'            <span class="obra-nav-titulo">{escape(siguiente["titulo"])}</span>',
        '        </a>',
        '    </nav>',
        '</main>',
    ]

    html = f"""<!DOCTYPE html>
<!-- Página generada por build.py a partir de data/obras.json: no editar a mano -->
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo_pagina}</title>
    <meta name="description" content="{descripcion}">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="es" href="{url_es}">
    <link rel="alternate" hreflang="en" href="{url_en}">
    <link rel="alternate" hreflang="x-default" href="{url_es}">

    <!-- Vista previa al compartir (WhatsApp, Instagram, Facebook…) -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Casanya">
    <meta property="og:locale" content="{t["locale"]}">
    <meta property="og:title" content="{titulo_pagina}">
    <meta property="og:description" content="{descripcion}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{imagen}">
    <meta property="og:image:width" content="{ancho}">
    <meta property="og:image:height" content="{alto}">
    <meta name="twitter:card" content="summary_large_image">

    <script type="application/ld+json">
{datos_estructurados(o, lang, ancho, alto)}
    </script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap">
    <link rel="stylesheet" href="../css/styles.css?v={version("css/styles.css")}">
    <link rel="icon" type="image/png" sizes="32x32" href="../images/ui/favicon-32.png">
    <link rel="apple-touch-icon" href="../images/ui/apple-touch-icon.png">
</head>
<body>

    <div class="site-container">
        <!-- CABECERA -->
        {cabecera}

{sangrar(principal, " " * 8)}

        {pie}
    </div>

    <script src="../js/inquire.js?v={version("js/inquire.js")}"></script>
</body>
</html>
"""
    destino = ROOT / pagina_obra(o, lang)
    destino.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- mapa del sitio

def generar_sitemap(obras):
    def url(f):
        return SITE if f == "index.html" else SITE + f
    pares = PAGINAS + [(pagina_obra(o, "es"), pagina_obra(o, "en")) for o in obras]
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
              '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for es, en in pares:
        for f in (es, en):
            lineas += ['  <url>',
                       f'    <loc>{url(f)}</loc>',
                       f'    <xhtml:link rel="alternate" hreflang="es" href="{url(es)}"/>',
                       f'    <xhtml:link rel="alternate" hreflang="en" href="{url(en)}"/>',
                       '  </url>']
    lineas.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return len(pares) * 2


# ---------------------------------------------------------------- principal

def main():
    obras = cargar_obras()

    for lang in IDIOMAS:
        generar_galeria(obras, lang)
    print(f"✓ Galería: {len(obras)} obras en index.html e index-en.html")

    # se vacía la carpeta para que no queden páginas de obras borradas de la lista
    carpeta = ROOT / "obras"
    if carpeta.exists():
        shutil.rmtree(carpeta)
    carpeta.mkdir()
    for n in range(len(obras)):
        for lang in IDIOMAS:
            generar_pagina_obra(obras, n, lang)
    print(f"✓ Páginas de obra: {len(obras) * 2} en obras/")

    total = generar_sitemap(obras)
    print(f"✓ sitemap.xml: {total} páginas")

    disponibles = sum(not o["vendida"] for o in obras)
    print(f"  {disponibles} disponibles, {len(obras) - disponibles} vendidas")


if __name__ == "__main__":
    main()
