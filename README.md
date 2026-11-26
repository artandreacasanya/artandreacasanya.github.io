# artandreacasanya.github.io

Website of Casanya (andreacasanya.com), served by GitHub Pages. Plain HTML and CSS. The gallery cards, one page per painting (`obras/`) and `sitemap.xml` are generated from `data/obras.json` by `build.py` (Python 3, no dependencies).

## Structure

```
*.html            pages (Spanish + *-en.html English); kept at the root so URLs don't change
css/styles.css    all styles; sizes are set in the :root block at the top
js/likes.js       "like" button (saved in the browser, counted in Google Sheets)
js/filters.js     gallery filters and availability counter
js/inquire.js     note with the email address under "Adquirir obra"
data/obras.json   the list of paintings (single source for both languages)
build.py          writes the gallery cards into index.html and index-en.html, obras/*.html and sitemap.xml
obras/            one page per painting and language (generated: do not edit by hand)
images/works/     painting photos, 1200 px on the long side
images/photos/    cover, about and process photos
images/ui/        logo, menu and title images, flags, hearts, favicon
```

## Adding a painting, marking it sold, changing a price

1. Resize the photo before adding it: `sips -Z 1200 -s formatOptions 75 photo.jpg`, and put it in `images/works/`.
2. Edit `data/obras.json` (add an entry, or change `vendida`, `precio`…). List order = order on the page, oldest first.
3. Run `python3 build.py`. It rewrites the cards between the `OBRAS:INICIO` / `OBRAS:FIN` markers in `index.html` and `index-en.html`, regenerates every page in `obras/` and `sitemap.xml`. Never edit those by hand.

Optional per painting: `texto` / `texto_en` (paragraphs separated by a blank line) are shown on its page.

## Previewing locally

`python3 -m http.server 8000` and open http://localhost:8000
