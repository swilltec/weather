from common.utils import get_city
from core.models import Client
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework.exceptions import AuthenticationFailed


class FingerprintAuthentication(BaseAuthentication):
    """
    Authenticates a client by fingerprint.
    The Client model acts as the authenticated user.
    """

    keyword = "X-Fingerprint"

    def authenticate(self, request):
        fingerprint = request.headers.get(self.keyword) or request.query_params.get(
            "fingerprint"
        )

        # Fallback: use entire Authorization header string
        if not fingerprint:
            auth = get_authorization_header(request).decode().strip()
            if not auth:
                raise AuthenticationFailed(
                    "Fingerprint header or Authorization missing"
                )
            fingerprint = auth

        client, _ = Client.objects.get_or_create(fingerprint=fingerprint)

        client.update_activity()

        # Attach client explicitly for convenience
        request.client = client

        # Client model becomes the authenticated user
        return (client, None)
