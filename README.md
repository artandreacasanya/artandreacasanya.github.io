# artandreacasanya.github.io

Website of Casanya (andreacasanya.com), served by GitHub Pages. Plain HTML and CSS, no build step.

## Structure

```
*.html            pages (Spanish + *-en.html English); kept at the root so URLs don't change
css/styles.css    all styles; sizes are set in the :root block at the top
js/likes.js       "like" button (saved in the browser, counted in Google Sheets)
images/works/     painting photos, 1200 px on the long side
images/photos/    cover, about and process photos
images/ui/        logo, menu and title images, flags, hearts, favicon
```

## Adding a painting

1. Resize the photo before adding it: `sips -Z 1200 -s formatOptions 75 photo.jpg`
2. Put it in `images/works/`.
3. Copy an existing `<article class="work-card">` in `index.html` and `index-en.html` and change the image, title, details and `data-work-id`.
