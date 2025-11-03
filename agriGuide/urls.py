from django.contrib import admin
from django.urls import path
from core.views import (
    welcome_view, login_view, register_view, logout_view, dashboard_view,
    chatbot_api, crop_prediction_api, superuser_login_view, translation_api, get_supported_languages_api, database_view
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome_view, name='welcome'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('superuser-login/', superuser_login_view, name='superuser_login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('database/', database_view, name='database'),
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
    path('api/crop-prediction/', crop_prediction_api, name='crop_prediction_api'),
    path('api/translate/', translation_api, name='translation_api'),
    path('api/languages/', get_supported_languages_api, name='supported_languages_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
