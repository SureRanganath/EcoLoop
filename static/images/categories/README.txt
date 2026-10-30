EcoLoop — category image slot
=============================

Drop an image for a material category in THIS folder using the category's
slug as the filename. That's it — no database change, no migration; the site
picks it up on the next page load (no server restart needed).

    static/images/categories/<slug>.<ext>

Accepted extensions — FIRST MATCH WINS, in this order:

    .webp   .jpg   .jpeg   .png   .svg

Because .webp is checked first, a generated .webp will always be served
before the .png/.svg in this folder.

CURRENT FILES
-------------
Per category there are two files:

    <slug>.webp   800x520, ~10-205 KB  <- actually served to browsers
    <slug>.png    1500x975, ~1-3.7 MB  <- your source art (kept, never served)

Total served weight: ~746 KB for all 8 (down from 17.8 MB of PNG).

If neither file exists for a slug, the card falls back to the category's
Bootstrap icon automatically (no broken images).

Category -> filename map:
    plastic.webp             -> Plastic
    metal.webp               -> Metal
    glass.webp               -> Glass
    textile.webp             -> Textile
    paper-cardboard.webp     -> Paper & Cardboard
    rubber.webp              -> Rubber
    organic-by-products.webp -> Organic By-products
    other-industrial.webp    -> Other Industrial

ADDING NEW / REPLACING ART
--------------------------
1. Add the file with the exact slug name, e.g. plastic.png (1500x975 or
   800x520 both work — anything is scaled/cropped to fill the card).
2. It will be served immediately ONLY if no .webp with that name exists.
   If a .webp is present it wins, so regenerate or delete the .webp when
   you swap in new art:
       python -c "from PIL import Image; from pathlib import Path; \
         p=Path('static/images/categories/plastic.png'); \
         Image.open(p).convert('RGB').resize((800,520)).save(p.with_suffix('.webp'),'WEBP',quality=82,method=6)"
3. Size target: 800x520 (aspect 1.538) — shown as a 104px-tall band on
   home cards and behind listing cards.

If a slug has no file at all, the site falls back to the category's
Bootstrap icon, so nothing ever breaks.

Viewed from: /static/images/categories/
