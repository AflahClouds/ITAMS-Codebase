"""Barcode rendering helper for Asset tag numbers."""
import os
import re

from django.conf import settings


def generate_asset_barcode(asset):
    """Render a Code128 PNG for the asset's tag number under MEDIA_ROOT/barcodes.

    Returns the path relative to MEDIA_ROOT (e.g. 'barcodes/2001001.png').
    """
    import barcode
    from barcode.writer import ImageWriter

    safe_tag = re.sub(r'[^A-Za-z0-9_-]', '_', str(asset.tag_number)) or f"asset_{asset.pk}"
    folder = os.path.join(settings.MEDIA_ROOT, 'barcodes')
    os.makedirs(folder, exist_ok=True)

    code = barcode.get('code128', str(asset.tag_number), writer=ImageWriter())
    # save() appends the extension itself
    saved = code.save(os.path.join(folder, safe_tag),
                      options={"module_height": 8.0, "font_size": 6, "text_distance": 3.0})
    return f"barcodes/{os.path.basename(saved)}"
