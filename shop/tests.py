from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from shop.models import Product, ProductOption, Tag


class ProductCreateAPITest(TestCase):
    """상품 생성 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.url = reverse("product-list")  # /shop/product/

        # 기존 태그 생성 (ExistTag)
        self.exist_tag = Tag.objects.create(name="ExistTag")

    def test_create_product_with_options_and_tags(self):
        """상품 생성 API 테스트 - 옵션과 태그 포함"""

        # 테스트 요청 데이터
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [
                {"pk": self.exist_tag.pk, "name": "ExistTag"},
                {"name": "NewTag"},
            ],
        }

        # API 요청
        response = self.client.post(self.url, request_data, format="json")

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 응답 데이터 구조 확인
        response_data = response.data
        self.assertIn("pk", response_data)
        self.assertIn("name", response_data)
        self.assertIn("option_set", response_data)
        self.assertIn("tag_set", response_data)

        # 상품명 확인
        self.assertEqual(response_data["name"], "TestProduct")

        # 옵션 개수 확인 (3개)
        self.assertEqual(len(response_data["option_set"]), 3)

        # 태그 개수 확인 (2개)
        self.assertEqual(len(response_data["tag_set"]), 2)

        # 옵션 데이터 확인
        option_names = [opt["name"] for opt in response_data["option_set"]]
        option_prices = [opt["price"] for opt in response_data["option_set"]]

        self.assertIn("TestOption1", option_names)
        self.assertIn("TestOption2", option_names)
        self.assertIn("TestOption3", option_names)

        self.assertIn(1000, option_prices)
        self.assertIn(500, option_prices)
        self.assertIn(0, option_prices)

        # 태그 데이터 확인
        tag_names = [tag["name"] for tag in response_data["tag_set"]]
        self.assertIn("ExistTag", tag_names)
        self.assertIn("NewTag", tag_names)

    def test_create_product_without_name(self):
        """상품명이 없는 경우 에러 테스트"""

        request_data = {"option_set": [], "tag_set": []}

        response = self.client.post(self.url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "상품명이 필요합니다.")

    def test_create_product_with_empty_data(self):
        """빈 데이터로 상품 생성 테스트"""

        request_data = {"name": "EmptyProduct", "option_set": [], "tag_set": []}

        response = self.client.post(self.url, request_data, format="json")

        # 성공적으로 생성
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "EmptyProduct")
        self.assertEqual(len(response.data["option_set"]), 0)
        self.assertEqual(len(response.data["tag_set"]), 0)

    def test_database_objects_created(self):
        """데이터베이스에 실제로 객체가 생성되었는지 확인"""

        # 초기 개수
        initial_product_count = Product.objects.count()
        initial_option_count = ProductOption.objects.count()
        initial_tag_count = Tag.objects.count()

        request_data = {
            "name": "TestProduct",
            "option_set": [{"name": "TestOption1", "price": 1000}],
            "tag_set": [{"name": "NewTag"}],
        }

        # API 요청
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 객체 개수 증가 확인
        self.assertEqual(Product.objects.count(), initial_product_count + 1)
        self.assertEqual(ProductOption.objects.count(), initial_option_count + 1)
        self.assertEqual(Tag.objects.count(), initial_tag_count + 1)

        # 생성된 상품 확인
        product = Product.objects.get(name="TestProduct")
        self.assertEqual(product.option_set.count(), 1)
        self.assertEqual(product.tag_set.count(), 1)

    def test_create_product_with_invalid_tag(self):
        """존재하지 않는 태그로 상품 생성 테스트"""

        request_data = {
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": 99999, "name": "NonExistentTag"}],
        }

        response = self.client.post(self.url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "태그를 찾을 수 없습니다.")

    def test_create_product_with_missing_option_fields(self):
        """옵션 필수 필드가 누락된 경우 테스트"""

        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "OptionWithoutPrice"},  # price 누락
            ],
            "tag_set": [],
        }

        response = self.client.post(self.url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])

    def test_create_product_with_invalid_price_type(self):
        """잘못된 가격 타입 테스트"""

        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption", "price": "not_a_number"},  # 문자열
            ],
            "tag_set": [],
        }

        response = self.client.post(self.url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("잘못된 데이터 형식입니다", response.data["message"])


class ProductUpdateAPITest(TestCase):
    """상품 수정 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()

        # 기존 태그 생성
        self.exist_tag = Tag.objects.create(name="ExistTag")
        self.new_tag = Tag.objects.create(name="NewTag")

        # 테스트 상품 생성
        self.product = Product.objects.create(name="OriginalProduct")
        self.product.tag_set.add(self.exist_tag)

        # 테스트 옵션 생성
        self.option1 = ProductOption.objects.create(
            product=self.product, name="OriginalOption1", price=1000
        )
        self.option2 = ProductOption.objects.create(
            product=self.product, name="OriginalOption2", price=2000
        )
        self.option3 = ProductOption.objects.create(
            product=self.product, name="OriginalOption3", price=3000
        )

    def test_update_product_success(self):
        """상품 수정 API 성공 테스트"""

        # 테스트 요청 데이터
        request_data = {
            "name": "UpdatedProduct",
            "option_set": [
                {"pk": self.option1.pk, "name": "UpdatedOption1", "price": 1500},
                {"pk": self.option2.pk, "name": "UpdatedOption2", "price": 2500},
                {"name": "NewOption", "price": 4000},
            ],
            "tag_set": [
                {"pk": self.exist_tag.pk, "name": "ExistTag"},
                {"pk": self.new_tag.pk, "name": "NewTag"},
                {"name": "AnotherNewTag"},
            ],
        }

        # API 요청
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        response_data = response.data
        self.assertEqual(response_data["name"], "UpdatedProduct")
        self.assertEqual(len(response_data["option_set"]), 3)
        self.assertEqual(len(response_data["tag_set"]), 3)

        # 옵션 데이터 확인
        option_names = [opt["name"] for opt in response_data["option_set"]]
        self.assertIn("UpdatedOption1", option_names)
        self.assertIn("UpdatedOption2", option_names)
        self.assertIn("NewOption", option_names)

        # 태그 데이터 확인
        tag_names = [tag["name"] for tag in response_data["tag_set"]]
        self.assertIn("ExistTag", tag_names)
        self.assertIn("NewTag", tag_names)
        self.assertIn("AnotherNewTag", tag_names)

    def test_update_product_not_found(self):
        """존재하지 않는 상품 수정 테스트"""

        request_data = {"name": "UpdatedProduct", "option_set": [], "tag_set": []}
        url = reverse("product-detail", kwargs={"pk": 99999})
        response = self.client.patch(url, request_data, format="json")

        # 404 Not Found 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "상품을 찾을 수 없습니다.")

    def test_update_product_with_invalid_tag(self):
        """존재하지 않는 태그로 수정 테스트"""

        request_data = {
            "name": "UpdatedProduct",
            "option_set": [],
            "tag_set": [{"pk": 99999, "name": "NonExistentTag"}],
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "태그를 찾을 수 없습니다.")

    def test_update_product_with_missing_fields(self):
        """필수 필드가 누락된 경우 테스트"""

        request_data = {
            "name": "UpdatedProduct",
            "option_set": [{"name": "OptionWithoutPrice"}],  # price 누락
            "tag_set": [],
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])

    def test_update_product_remove_options(self):
        """옵션 삭제 테스트"""

        # 기존 3개 옵션에서 1개만 남기고 삭제
        request_data = {
            "name": "UpdatedProduct",
            "option_set": [
                {"pk": self.option1.pk, "name": "KeepThisOption", "price": 1000}
            ],
            "tag_set": [],
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["option_set"]), 1)
        self.assertEqual(response.data["option_set"][0]["name"], "KeepThisOption")

    def test_update_product_name_only(self):
        """상품명만 수정하는 테스트"""

        request_data = {"name": "OnlyNameChanged"}
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OnlyNameChanged")
        # 기존 옵션과 태그는 모두 삭제됨 (다 지우고 재생성 방식)
        self.assertEqual(len(response.data["option_set"]), 0)
        self.assertEqual(len(response.data["tag_set"]), 0)
