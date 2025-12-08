import uuid

from core.constants import MessageType, TemperatureUnit, WindSpeedUnit
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class BaseAbstractModel(models.Model):
    """Base model for all models."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_updated = models.DateTimeField(auto_now=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Class meta."""

        abstract = True


class Client(BaseAbstractModel):
    """
    Represents a unique visitor identified by Fingerprint JS.

    Each client is uniquely identified by their browser fingerprint,
    allowing anonymous tracking of user preferences and search history
    without requiring authentication.
    """

    fingerprint = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique fingerprint ID from Fingerprint JS API. This identifies the browser/device.",
    )
    last_seen = models.DateTimeField(
        auto_now=True, help_text="Timestamp of the client's most recent activity"
    )
    total_requests = models.PositiveIntegerField(
        default=0, help_text="Total number of weather/chat requests made by this client"
    )
    user_agent = models.TextField(
        blank=True, help_text="Browser user agent string for analytics and debugging"
    )

    class Meta:
        ordering = ["-last_seen"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"Client {self.fingerprint[:16]}... (Last seen: {self.last_seen})"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def update_activity(self):
        """
        Update the client's activity tracking.

        Updates the last_seen timestamp to current time and increments
        the total_requests counter. Should be called on each interaction.

        Returns:
            None
        """
        self.total_requests += 1
        self.save(update_fields=["last_seen", "total_requests"])


class City(BaseAbstractModel):
    """
    Stores cities that clients have searched for weather information.

    Each city is linked to a specific client and stores geographic coordinates
    for weather API lookups. Tracks search frequency and favorite status
    for personalized user experience.
    """

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="cities",
        help_text="The client who searched for this city",
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="City name (e.g., 'London', 'New York', 'Tokyo')",
    )
    country_code = models.CharField(
        max_length=2,
        blank=True,
        help_text="ISO 3166-1 alpha-2 country code (e.g., 'GB', 'US', 'JP')",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Geographic latitude (-90 to 90 degrees). Example: 51.507351 for London",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Geographic longitude (-180 to 180 degrees). Example: -0.127758 for London",
    )
    search_count = models.PositiveIntegerField(
        default=1, help_text="Number of times this client has searched for this city"
    )
    last_searched = models.DateTimeField(
        auto_now=True, help_text="Timestamp of the most recent search for this city"
    )
    is_favorite = models.BooleanField(
        default=False, help_text="Whether the client has marked this city as a favorite"
    )

    class Meta:
        ordering = ["-last_searched"]
        verbose_name = "City"
        verbose_name_plural = "Cities"
        unique_together = [["client", "name", "country_code"]]

    def __str__(self):
        return f"{self.name} ({self.country_code}) - {self.client.fingerprint[:8]}..."

    def increment_search(self):
        """
        Increment the search counter for this city.

        Updates search_count and last_searched timestamp when a client
        searches for this city again. Useful for tracking popular locations
        and providing quick access to frequently searched cities.

        Returns:
            None
        """
        self.search_count += 1
        self.last_searched = timezone.now()
        self.save(update_fields=["search_count", "last_searched"])


# class WeatherCache(BaseAbstractModel):
#     """
#     Caches weather data to reduce external API calls and improve performance.

#     Stores the most recent weather information for each city. Data is
#     automatically refreshed when it becomes stale (default: 30 minutes).
#     This reduces costs and improves response times.

#     Attributes:
#         city (OneToOneField): The city this weather data is for
#         temperature (Decimal): Current temperature in Celsius
#         feels_like (Decimal): "Feels like" temperature in Celsius
#         humidity (int): Humidity percentage (0-100)
#         pressure (int): Atmospheric pressure in hPa
#         wind_speed (Decimal): Wind speed in m/s
#         description (str): Weather condition description
#         icon_code (str): Weather icon code from API
#         cached_at (datetime): When this data was cached
#     """

#     city = models.OneToOneField(
#         City,
#         on_delete=models.CASCADE,
#         related_name='weather_cache',
#         help_text="The city this weather data belongs to"
#     )
#     temperature = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         help_text="Current temperature in Celsius (e.g., 23.50)"
#     )
#     feels_like = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         help_text="'Feels like' temperature in Celsius accounting for humidity and wind"
#     )
#     humidity = models.PositiveSmallIntegerField(
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         help_text="Relative humidity percentage (0-100)"
#     )
#     pressure = models.PositiveIntegerField(
#         help_text="Atmospheric pressure in hectopascals (hPa)"
#     )
#     wind_speed = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         help_text="Wind speed in meters per second (m/s)"
#     )
#     description = models.CharField(
#         max_length=100,
#         help_text="Weather condition description (e.g., 'clear sky', 'light rain')"
#     )
#     icon_code = models.CharField(
#         max_length=10,
#         blank=True,
#         help_text="Weather icon code from API (e.g., '01d' for clear sky day)"
#     )
#     cached_at = models.DateTimeField(
#         auto_now=True,
#         help_text="Timestamp when this weather data was last updated"
#     )

#     class Meta:
#         verbose_name = "Weather Cache"
#         verbose_name_plural = "Weather Caches"

#     def __str__(self):
#         return f"Weather for {self.city.name} (cached {self.cached_at})"

#     def is_stale(self, minutes=30):
#         """
#         Check if the cached weather data needs refreshing.

#         Args:
#             minutes (int): Cache validity duration in minutes (default: 30)

#         Returns:
#             bool: True if cache is older than specified minutes, False otherwise

#         Example:
#             >>> cache.is_stale(30)  # Check if older than 30 minutes
#             True
#             >>> cache.is_stale(60)  # Check if older than 1 hour
#             False
#         """
#         return (timezone.now() - self.cached_at).total_seconds() > (minutes * 60)


class Conversation(BaseAbstractModel):
    """
    Represents a chat conversation session between a client and the weather bot.

    Each conversation groups related messages together, allowing context-aware
    responses and conversation history tracking. Conversations can be archived
    or marked inactive after periods of inactivity.

    Attributes:
        client (ForeignKey): The client participating in this conversation
        started_at (datetime): When the conversation began
        last_message_at (datetime): Timestamp of the most recent message
        message_count (int): Total number of messages in this conversation
        is_active (bool): Whether the conversation is currently active
    """

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="conversations",
        help_text="The client who initiated this conversation",
    )
    started_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when this conversation was started"
    )
    last_message_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the most recent message in this conversation",
    )
    message_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of messages (user + bot) in this conversation",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this conversation is currently active. Inactive conversations can be archived.",
    )

    class Meta:
        ordering = ["-last_message_at"]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return f"Conversation {self.id} - {self.client.fingerprint[:8]}... ({self.message_count} messages)"


class Message(BaseAbstractModel):
    """
    Stores individual chat messages within a conversation.

    Messages can be from the user, bot responses, or system notifications.
    Each message is timestamped and can be linked to a specific city for
    context-aware weather discussions.

    Attributes:
        conversation (ForeignKey): The conversation this message belongs to
        message_type (str): Type of message (USER, BOT, or SYSTEM)
        content (str): The actual message text
        timestamp (datetime): When the message was sent
        related_city (ForeignKey): Optional city mentioned in the message
        was_helpful (bool): Optional user feedback on bot response quality
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="message_conversation",
        help_text="The conversation this message is part of",
    )
    message_type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.USER,
        help_text="Type of message: USER (from client), BOT (response), or SYSTEM (notification)",
    )
    content = models.TextField(
        help_text="The actual message text or bot response content"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, help_text="Exact timestamp when this message was created"
    )
    related_city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_related_city",
        help_text="Optional: The city being discussed in this message for context",
    )
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="User feedback: whether the bot's response was helpful (True/False/None)",
    )

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.message_type}: {preview}"


class UserPreference(BaseAbstractModel):
    """
    Stores user preferences for personalized weather experience.

    Allows clients to customize their weather display units, set a default
    city, and configure notification preferences. Preferences persist across
    sessions using the fingerprint ID.

    Attributes:
        client (OneToOneField): The client these preferences belong to
        temperature_unit (str): Preferred temperature unit (C/F/K)
        wind_speed_unit (str): Preferred wind speed unit (kmh/mph/ms)
        default_city (ForeignKey): Optional default city to show on load
        show_forecast (bool): Whether to display weather forecast
        enable_notifications (bool): Whether to enable weather alerts
    """

    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name="preferences",
        help_text="The client these preferences belong to",
    )
    temperature_unit = models.CharField(
        max_length=1,
        choices=TemperatureUnit.choices,
        default=TemperatureUnit.CELSIUS,
        help_text="Preferred temperature unit: Celsius (C), Fahrenheit (F), or Kelvin (K)",
    )
    wind_speed_unit = models.CharField(
        max_length=3,
        choices=WindSpeedUnit.choices,
        default=WindSpeedUnit.KMH,
        help_text="Preferred wind speed unit: km/h, mph, or m/s",
    )
    default_city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_for_users",
        help_text="Optional: Default city to display when the user opens the app",
    )
    show_forecast = models.BooleanField(
        default=True,
        help_text="Whether to display weather forecast in addition to current weather",
    )
    enable_notifications = models.BooleanField(
        default=False,
        help_text="Whether to enable weather alert notifications for saved cities",
    )

    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"Preferences for {self.client.fingerprint[:8]}..."


class WeatherAlert(BaseAbstractModel):
    """
    Stores weather alerts and warnings for specific cities.

    Captures severe weather notifications from weather APIs or manual entry.
    Alerts have severity levels and time validity periods. Used to notify
    users about potentially dangerous weather conditions.

    Attributes:
        city (ForeignKey): The city this alert applies to
        title (str): Brief alert title/headline
        description (str): Detailed alert description
        severity (str): Alert severity level (LOW/MODERATE/HIGH/SEVERE)
        start_time (datetime): When the alert becomes active
        end_time (datetime): When the alert expires
        is_active (bool): Whether the alert is currently active
    """

    class AlertSeverity(models.TextChoices):
        """
        Weather alert severity levels.

        LOW: Minor weather advisory
        MODERATE: Weather watch or advisory
        HIGH: Weather warning
        SEVERE: Extreme weather warning
        """

        LOW = "LOW", "Low"
        MODERATE = "MODERATE", "Moderate"
        HIGH = "HIGH", "High"
        SEVERE = "SEVERE", "Severe"

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="alerts",
        help_text="The city this weather alert applies to",
    )
    title = models.CharField(
        max_length=255,
        help_text="Brief alert headline (e.g., 'Thunderstorm Warning', 'Heat Advisory')",
    )
    description = models.TextField(
        help_text="Detailed description of the weather alert and recommended actions"
    )
    severity = models.CharField(
        max_length=10,
        choices=AlertSeverity.choices,
        default=AlertSeverity.MODERATE,
        help_text="Alert severity level: LOW, MODERATE, HIGH, or SEVERE",
    )
    start_time = models.DateTimeField(help_text="When this alert becomes active")
    end_time = models.DateTimeField(
        help_text="When this alert expires or is no longer valid"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this alert is currently active. Can be manually deactivated.",
    )

    class Meta:
        ordering = ["-severity", "-start_time"]
        verbose_name = "Weather Alert"
        verbose_name_plural = "Weather Alerts"

    def __str__(self):
        return f"{self.severity} Alert: {self.title} - {self.city.name}"

    def is_current(self):
        """
        Check if the alert is currently valid.

        Verifies that:
        1. The alert is marked as active
        2. Current time is between start_time and end_time

        Returns:
            bool: True if alert is currently valid and should be displayed

        Example:
            >>> alert.is_current()
            True  # Alert is active and within validity period
        """
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time
