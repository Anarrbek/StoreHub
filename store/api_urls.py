from rest_framework import routers
from django.urls import path, include
from .views import CategoryViewSet, ProductViewSet, AIChatView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="ProjectZT API",
        default_version='v1',
        description="API для магазина ProjectZT",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger(<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('chat/', AIChatView.as_view(), name='ai_chat'),
]
