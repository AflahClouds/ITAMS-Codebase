"""Audit logging, notification and barcode helpers."""
import os
import re

from django.conf import settings

from .models import AuditLog, Notification


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


def get_profile(request):
    """Employee profile linked to the authenticated account (or None)."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "profile", None)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def log_action(request, action, module, old_value="", new_value=""):
    profile = get_profile(request)
    username = ""
    if getattr(request, "user", None) and request.user.is_authenticated:
        username = request.user.username
    AuditLog.objects.create(
        user=profile,
        username=username,
        action=action,
        module=module,
        old_value=old_value or "",
        new_value=new_value or "",
        ip_address=client_ip(request),
    )


def notify(profile, message, link=""):
    if profile is None:
        return
    Notification.objects.create(user=profile, message=message, link=link or "")
