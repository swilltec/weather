from core.api.mixins import ClientFilteredQuerysetMixin
from core.api.serializers import (
    CitySerializer,
    ConversationSerializer,
    MessageSerializer,
    UserPreferenceSerializer,
)
from core.models import City, Client, Conversation, Message, UserPreference
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, generics

# from core.api.serializers import (
#     ClientSerializer, CitySerializer, WeatherCacheSerializer,
#     ConversationSerializer, MessageSerializer, UserPreferenceSerializer,
#     WeatherAlertSerializer
# )


class BaseViewSet(ClientFilteredQuerysetMixin, ModelViewSet):
    filter_backends = [SearchFilter, OrderingFilter]


class CityViewSet(BaseViewSet):
    queryset = City.objects.select_related("client").order_by("-last_searched")
    serializer_class = CitySerializer
    search_fields = ["name", "country_code"]
    ordering_fields = ["last_searched", "search_count", "datetime_created"]


class ConversationViewSet(BaseViewSet):
    queryset = Conversation.objects.select_related("client").order_by(
        "-last_message_at"
    )
    serializer_class = ConversationSerializer
    search_fields = ["client__fingerprint"]
    ordering_fields = ["last_message_at", "message_count"]


class MessageViewSet(BaseViewSet):
    queryset = Message.objects.select_related(
        "conversation", "conversation__client", "related_city"
    ).order_by("timestamp")
    serializer_class = MessageSerializer
    search_fields = ["content"]
    ordering_fields = ["timestamp"]


class UserPreferenceViewSet(BaseViewSet):
    queryset = UserPreference.objects.select_related("client", "default_city")
    serializer_class = UserPreferenceSerializer
