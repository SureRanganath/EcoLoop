"""Template tags for optional static artwork.

Category images are resolved from static files by convention, so no model
field or migration is needed:

    static/images/categories/<category-slug>.<ext>

Drop a file in with the matching slug and it appears across the site
(home category grid, marketplace, listing detail, favourites). When no
file exists, templates fall back to the category's Bootstrap icon.
"""
from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()

# Tried in order; first match wins. Use .webp or .jpg for photos, .svg for art.
IMAGE_EXTENSIONS = ('.webp', '.jpg', '.jpeg', '.png', '.svg')

IMAGE_DIR = 'images/categories/'


def _resolve(slug):
    """Resolve slug -> static URL.

    Deliberately uncached: a miss must be re-checked on every render so a
    file dropped into the folder while the dev server is running shows up
    immediately instead of after a restart.
    """
    for ext in IMAGE_EXTENSIONS:
        path = f'{IMAGE_DIR}{slug}{ext}'
        if finders.find(path):
            return static(path)
    return ''


@register.simple_tag
def category_image(category):
    """Return the static URL of a category's image, or '' when none exists."""
    if category is None:
        return ''
    slug = getattr(category, 'slug', '') or ''
    if not slug:
        return ''
    return _resolve(slug)
