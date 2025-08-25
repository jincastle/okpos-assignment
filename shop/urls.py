from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet

# 라우터 설정
product_router = DefaultRouter()
product_router.register(r"product", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(product_router.urls)),
]
