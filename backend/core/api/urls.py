from core.api import views
from django.urls import include, path
from rest_framework import routers

app_name = "core"

router = routers.DefaultRouter()

router.register(r"clients", views.CityViewSet, basename="client")
router.register(r"cities", views.CityViewSet, basename="city")
router.register(r"conversations", views.ConversationViewSet, basename="conversation")
router.register(r"messages", views.MessageViewSet, basename="message")
router.register(r"preferences", views.UserPreferenceViewSet, basename="userpreference")
# router.register(r'alerts', views.WeatherAlertViewSet, basename='weatheralert')


urlpatterns = [
    path("", include(router.urls)),
]
