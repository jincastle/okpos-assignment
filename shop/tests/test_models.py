from django.test import TestCase
from shop.models import Tag, Product, ProductOption


class ModelTest(TestCase):
    """모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.tag = Tag.objects.create(name="TestTag")
        self.product = Product.objects.create(name="TestProduct")
        self.option = ProductOption.objects.create(
            product=self.product, name="TestOption", price=1000
        )

    def test_model_str_methods(self):
        """모델의 __str__ 메서드 테스트"""
        # 각 모델의 __str__ 메서드 테스트
        test_cases = [
            (self.tag, "TestTag"),
            (self.product, "TestProduct"),
            (self.option, "TestOption"),
        ]
        
        for instance, expected_str in test_cases:
            with self.subTest(instance=instance):
                self.assertEqual(str(instance), expected_str)
