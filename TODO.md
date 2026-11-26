# TODO — andreacasanya.com

Mejoras pendientes, de mayor a menor prioridad. Marca cada una con `[x]` al terminarla.

## 1. Prioridad alta: se nota mucho y cuesta poco

- [x] **Cargar la tipografía real.** El CSS usa «Minion Variable Concept», pero la fuente no se carga desde la web, así que casi todos los visitantes ven Georgia. Cargarla desde Adobe Fonts (si hay licencia) o sustituirla por una parecida de Google Fonts (*Crimson Pro*, *EB Garamond*).
- [x] **Etiquetas para compartir (Open Graph).** Añadir `og:title`, `og:description`, `og:image` y `meta description` en cada página, para que los enlaces en WhatsApp e Instagram salgan con imagen y texto.
- [x] **Contraste de los textos grises.** «Consultar envío», «Marco artesanal incluido», el contador y el pie de página usan `#888` o `opacity: 0.7` en tamaño pequeño, y no llegan al contraste mínimo recomendado. Oscurecerlos a `#666`.
- [x] **Mostrar el correo como texto** junto a los botones de «Adquirir obra»: el `mailto:` no funciona si el visitante no tiene un programa de correo configurado.

## 2. Prioridad media-alta: experiencia de compra

- [x] **Ampliar las obras.** Al pulsar una obra se abre su página, con la foto grande y la ficha completa.
- [x] **Página propia para cada obra**, con varias fotos (detalle de la pincelada, canto, obra colgada en una pared), ficha completa y botón de compra. Esas páginas se pueden compartir por enlace y las encuentra Google.
- [x] **Formulario de contacto** (por ejemplo Formspree, gratis y sin servidor) como alternativa al `mailto:`.

## 3. Organización: ahorra tiempo al mantener la web

- [x] **Una sola lista de obras** (en lugar de Jekyll): `data/obras.json` con título, precio, medidas, año y estado de cada obra; `python3 build.py` genera las tarjetas en español e inglés. Sin instalar nada.
- [x] **Una fecha por obra** (mes y año) en lugar de solo el año. Ahora el filtro por fecha usa el orden de la página como orden cronológico.
- [ ] **Correo con dominio propio** (`hola@andreacasanya.com` en lugar de Gmail). Aplazado: la opción recomendada es una redirección gratuita a Gmail.

## 4. Optimización

- [ ] **Imágenes WebP con `srcset`**, para que el móvil descargue versiones más pequeñas.
- [ ] **Añadir `width` y `height` a las `<img>`**, para que la página no «salte» mientras cargan las fotos.
- [ ] **Menú y títulos en SVG** (o con una fuente manuscrita) en lugar de 20 imágenes PNG (876 KB). Pesan menos, se ven nítidos en cualquier pantalla y Google puede leerlos.
- [ ] **Reducir el favicon** de 138 KB a unos 5 KB.

## 5. SEO y aspectos técnicos

- [x] **`hreflang`** en cada página, para enlazar entre sí las versiones en español e inglés.
- [x] **`sitemap.xml` y `robots.txt`.**
- [ ] **Página `404.html`** con el diseño de la web.
- [x] **Datos estructurados** (`VisualArtwork` de schema.org) para cada obra.
- [ ] **Año del copyright** del pie de página actualizado automáticamente.

## 6. Contenido y confianza

- [ ] **Ampliar «Sobre mí»**: trayectoria, formación, exposiciones, prensa.
- [ ] **Unificar el trato** en los textos: ahora se mezcla «¿Hacéis…?» / «¿Tienen…?» con «¿Haces…?» / «trabajo sobre series…».
- [ ] **Estadísticas de visitas** respetuosas con la privacidad (GoatCounter: gratis y sin cookies).
- [ ] **Decidir qué hacer con los «me gusta»**: el recuento no se muestra a nadie, y cualquiera podría enviar «me gustas» falsos a la hoja de Google. Mostrar el número o quitar la función.
- [ ] **Acceso anticipado como suscripción real** (Buttondown, Mailchimp) si se recupera ese apartado.

## 7. Pendientes de información

- [ ] **Preguntas frecuentes comentadas** en `contacto.html` y `contact-en.html`: «¿Hacéis envíos internacionales? ¿Tendré seguimiento?» y «¿Puedo comprar prints o reproducciones?». Escribir la respuesta y borrar el comentario.
- [x] **Aviso legal**: quitada la mención a las «solicitudes de acceso anticipado» y añadido el formulario (FormSubmit). Completada la versión inglesa, que estaba cortada.
- [ ] **Datos personales en el aviso legal**: el NIF y el domicilio son públicos. Confirmar con la titular qué exige la LSSI y si está de acuerdo en publicarlos.
- [x] **Revisar las traducciones al inglés**: correctas. Mejorados «Shipping inquiries», «Sold», «Acquire this work» y el texto de envíos; arreglado el enlace a la sección de envíos.
