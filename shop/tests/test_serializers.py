from django.test import TestCase
from shop.models import Tag, Product, ProductOption
from shop.serializers import (
    TagSerializer,
    ProductOptionSerializer,
    ProductCreateSerializer,
)


class SerializerTest(TestCase):
    """시리얼라이저 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.tag = Tag.objects.create(name="TestTag")
        self.product = Product.objects.create(name="TestProduct")
        self.option = ProductOption.objects.create(
            product=self.product, name="TestOption", price=1000
        )

    def test_tag_serializer(self):
        """Tag 시리얼라이저 테스트"""
        serializer = TagSerializer(self.tag)
        self.assertEqual(serializer.data["name"], "TestTag")

    def test_product_option_serializer(self):
        """ProductOption 시리얼라이저 테스트"""
        serializer = ProductOptionSerializer(self.option)
        self.assertEqual(serializer.data["name"], "TestOption")
        self.assertEqual(serializer.data["price"], 1000)

    def test_product_create_serializer(self):
        """ProductCreate 시리얼라이저 테스트"""
        # 태그와 옵션 연결
        self.product.tag_set.add(self.tag)

        serializer = ProductCreateSerializer(self.product)
        self.assertEqual(serializer.data["name"], "TestProduct")
        self.assertEqual(len(serializer.data["tag_set"]), 1)
        self.assertEqual(len(serializer.data["option_set"]), 1)
