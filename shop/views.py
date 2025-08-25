from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.response import Response

from shop.models import Product, ProductOption, Tag
from shop.serializers import ProductCreateSerializer


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    http_method_names = ['post']

    # 상품 생성 API
    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get("name")
            option_set = request.data.get("option_set", [])
            tag_set = request.data.get("tag_set", [])

            # 상품명 검증
            if not name:
                return Response(
                    {"message": "상품명이 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 트랜잭션으로 데이터 생성
            with transaction.atomic():
                # 상품 생성
                product = Product.objects.create(name=name)

                # 옵션 생성
                for option_data in option_set:
                    ProductOption.objects.create(
                        product=product,
                        name=option_data["name"],
                        price=option_data["price"],
                    )

                # 태그 처리
                for tag_data in tag_set:
                    if "pk" in tag_data:
                        tag = Tag.objects.get(pk=tag_data["pk"])
                    else:
                        tag, created = Tag.objects.get_or_create(name=tag_data["name"])
                    product.tag_set.add(tag)

            # N+1 문제 해결
            product = (
                Product.objects.select_related()
                .prefetch_related("option_set", "tag_set")
                .get(pk=product.pk)
            )

            # 응답 데이터 생성
            serializer = ProductCreateSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
