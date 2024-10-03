import hmac
import hashlib
from django.conf import settings

def consistent_encrypt(value):
    """Encrypt a value consistently using HMAC."""
    return hmac.new(settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()