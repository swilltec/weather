class ClientFilteredQuerysetMixin:
    """
    Automatically filters queryset so only objects belonging to the
    authenticated Client (request.user) are returned.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        client = getattr(self.request, "user", None)

        if not client or getattr(self, "swagger_fake_view", False):
            return qs.none()

        # Direct FK: model has `client`
        if hasattr(self.queryset.model, "client_id"):
            return qs.filter(client=client)

        # Message → Conversation → Client
        if hasattr(self.queryset.model, "conversation_id"):
            return qs.filter(conversation__client=client)

        # Default: no filtering possible
        return qs
