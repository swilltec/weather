from core.models import City, Client, Conversation, Message, UserPreference
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "fingerprint",
            "last_seen",
            "total_requests",
            "user_agent",
            "datetime_created",
            "datetime_updated",
        ]
        read_only_fields = [
            "last_seen",
            "total_requests",
            "datetime_created",
            "datetime_updated",
        ]


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = [
            "id",
            "client",
            "name",
            "country_code",
            "latitude",
            "longitude",
            "search_count",
            "last_searched",
            "is_favorite",
            "datetime_created",
            "datetime_updated",
        ]
        read_only_fields = [
            "search_count",
            "last_searched",
            "datetime_created",
            "datetime_updated",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "id",
            "client",
            "started_at",
            "last_message_at",
            "message_count",
            "is_active",
            "datetime_created",
            "datetime_updated",
        ]
        read_only_fields = [
            "started_at",
            "last_message_at",
            "message_count",
            "datetime_created",
            "datetime_updated",
        ]


class UserPreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPreference
        fields = [
            "id",
            "client",
            "temperature_unit",
            "wind_speed_unit",
            "default_city",
            "show_forecast",
            "enable_notifications",
            "datetime_created",
            "datetime_updated",
        ]
        read_only_fields = ["datetime_created", "datetime_updated"]


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "message_type",
            "content",
            "timestamp",
            "related_city",
            "was_helpful",
            "datetime_created",
            "datetime_updated",
        ]
        read_only_fields = ["timestamp", "datetime_created", "datetime_updated"]


class AlertSerializer(serializers.Serializer):
    city = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    description = serializers.CharField()
    severity = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    is_active = serializers.BooleanField()
