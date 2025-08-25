from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 문서화 설정
schema_view = get_schema_view(
    openapi.Info(
        title="OKPOS Assignment API",
        default_version='v1',
        description="상품 관리 API 문서",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    
    # API 문서화
    path('doc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-swagger-ui'),
]
