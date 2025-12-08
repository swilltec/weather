from common.utils import get_city
from core.models import Client
from rest_framework.authentication import BaseAuthentication
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

        if not fingerprint:
            raise AuthenticationFailed("Fingerprint header missing")


        client, created = Client.objects.get_or_create(fingerprint=fingerprint)

        client.update_activity()

        # Attach client explicitly for convenience
        request.client = client

        # Client model becomes the authenticated user
        return (client, None)
