from core.models import (City, Client, Conversation, Message, UserPreference,
                         WeatherAlert)
from django.contrib import admin


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("fingerprint", "last_seen", "total_requests")
    search_fields = ("fingerprint", "user_agent")
    readonly_fields = ("datetime_updated", "total_requests")
    ordering = ("-datetime_updated",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "country_code",
        "client",
        "search_count",
        "last_searched",
        "is_favorite",
    )
    search_fields = ("name", "country_code", "client__fingerprint")
    list_filter = ("country_code", "is_favorite")
    readonly_fields = ("last_searched", "search_count")
    ordering = ("-last_searched",)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("timestamp",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "started_at",
        "last_message_at",
        "message_count",
        "is_active",
    )
    search_fields = ("client__fingerprint",)
    list_filter = ("is_active",)
    readonly_fields = ("started_at", "last_message_at", "message_count")
    inlines = [MessageInline]
    ordering = ("-last_message_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "message_type",
        "conversation",
        "timestamp",
        "related_city",
        "was_helpful",
    )
    search_fields = ("content", "conversation__id", "related_city__name")
    list_filter = ("message_type", "was_helpful")
    readonly_fields = ("timestamp",)
    ordering = ("timestamp",)


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "temperature_unit",
        "wind_speed_unit",
        "default_city",
        "show_forecast",
        "enable_notifications",
    )
    search_fields = ("client__fingerprint", "default_city__name")
    list_filter = (
        "temperature_unit",
        "wind_speed_unit",
        "show_forecast",
        "enable_notifications",
    )


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "severity", "start_time", "end_time", "is_active")
    search_fields = ("title", "city__name")
    list_filter = ("severity", "is_active", "start_time")
    ordering = ("-severity", "-start_time")
