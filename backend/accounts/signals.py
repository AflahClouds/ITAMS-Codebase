"""Login-token revocation for deactivated employee profiles.

HasRolePermission already refuses a request whose profile is not Active, so a
disabled user is blocked at every endpoint that uses it. That is a check every
future endpoint has to remember to apply — /dashboard/ and /charts/ did not, and
a disabled user kept reading them with a token issued before deactivation.
Dropping the token removes the standing credential instead of relying on each
call site to reject it.

Wired as a post_save receiver rather than done in UserViewSet because status is
editable from the Django admin and the shell as well as the API.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import User


@receiver(post_save, sender=User, dispatch_uid="accounts.revoke_tokens_on_deactivate")
def revoke_tokens_on_deactivate(sender, instance, **kwargs):
    if instance.status == "Active" or instance.account_id is None:
        return
    Token.objects.filter(user_id=instance.account_id).delete()
