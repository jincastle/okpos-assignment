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
        """상품 수정 API 성공 테스트 (전체 필드 수정)"""

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

    def test_update_product_name_only(self):
        """상품명만 수정하는 테스트"""

        request_data = {"name": "OnlyNameChanged"}
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OnlyNameChanged")
        # 기존 옵션과 태그는 유지됨 (PATCH 방식)
        self.assertEqual(len(response.data["option_set"]), 3)
        self.assertEqual(len(response.data["tag_set"]), 1)

    def test_update_product_options_only(self):
        """옵션만 수정하는 테스트"""

        request_data = {
            "option_set": [
                {"name": "NewOption1", "price": 500},
                {"name": "NewOption2", "price": 1000},
            ]
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OriginalProduct")  # 기존 이름 유지
        self.assertEqual(len(response.data["option_set"]), 2)  # 새 옵션 2개
        self.assertEqual(len(response.data["tag_set"]), 1)  # 기존 태그 유지

    def test_update_product_tags_only(self):
        """태그만 수정하는 테스트"""

        request_data = {
            "tag_set": [
                {"name": "NewTag1"},
                {"name": "NewTag2"},
            ]
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OriginalProduct")  # 기존 이름 유지
        self.assertEqual(len(response.data["option_set"]), 3)  # 기존 옵션 유지
        self.assertEqual(len(response.data["tag_set"]), 2)  # 새 태그 2개

    def test_update_product_remove_options(self):
        """옵션을 빈 리스트로 초기화하는 테스트"""

        request_data = {"option_set": []}
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OriginalProduct")  # 기존 이름 유지
        self.assertEqual(len(response.data["option_set"]), 0)  # 옵션 모두 삭제
        self.assertEqual(len(response.data["tag_set"]), 1)  # 기존 태그 유지

    def test_update_product_remove_tags(self):
        """태그를 빈 리스트로 초기화하는 테스트"""

        request_data = {"tag_set": []}
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OriginalProduct")  # 기존 이름 유지
        self.assertEqual(len(response.data["option_set"]), 3)  # 기존 옵션 유지
        self.assertEqual(len(response.data["tag_set"]), 0)  # 태그 모두 삭제

    def test_update_product_not_found(self):
        """존재하지 않는 상품 수정 테스트"""

        request_data = {"name": "UpdatedProduct"}
        url = reverse("product-detail", kwargs={"pk": 99999})
        response = self.client.patch(url, request_data, format="json")

        # 404 Not Found 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "상품을 찾을 수 없습니다.")

    def test_update_product_with_invalid_tag(self):
        """존재하지 않는 태그로 수정 테스트"""

        request_data = {
            "tag_set": [{"pk": 99999, "name": "NonExistentTag"}]
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "태그를 찾을 수 없습니다.")

    def test_update_product_with_missing_fields(self):
        """옵션 필수 필드가 누락된 경우 테스트"""

        request_data = {
            "option_set": [{"name": "OptionWithoutPrice"}]  # price 누락
        }
        url = reverse("product-detail", kwargs={"pk": self.product.pk})
        response = self.client.patch(url, request_data, format="json")

        # 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])


class ProductListAPITest(TestCase):
    """상품 목록 조회 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        
        # 기존 태그 생성
        self.tag1 = Tag.objects.create(name="Tag1")
        self.tag2 = Tag.objects.create(name="Tag2")
        
        # 테스트 상품 1 생성
        self.product1 = Product.objects.create(name="Product1")
        self.product1.tag_set.add(self.tag1)
        
        # 테스트 상품 1의 옵션 생성
        self.option1_1 = ProductOption.objects.create(
            product=self.product1, name="Option1_1", price=1000
        )
        self.option1_2 = ProductOption.objects.create(
            product=self.product1, name="Option1_2", price=2000
        )
        
        # 테스트 상품 2 생성 (옵션/태그 없음)
        self.product2 = Product.objects.create(name="Product2")

    def test_get_product_list_success(self):
        """상품 목록 조회 성공 테스트"""

        # API 요청
        url = reverse("product-list")
        response = self.client.get(url)

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 구조 확인
        response_data = response.data
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 2)  # 상품 2개

        # 첫 번째 상품 데이터 확인
        product1_data = response_data[0]
        self.assertIn("pk", product1_data)
        self.assertIn("name", product1_data)
        self.assertIn("option_set", product1_data)
        self.assertIn("tag_set", product1_data)
        self.assertEqual(product1_data["name"], "Product1")
        self.assertEqual(len(product1_data["option_set"]), 2)
        self.assertEqual(len(product1_data["tag_set"]), 1)

        # 두 번째 상품 데이터 확인
        product2_data = response_data[1]
        self.assertEqual(product2_data["name"], "Product2")
        self.assertEqual(len(product2_data["option_set"]), 0)
        self.assertEqual(len(product2_data["tag_set"]), 0)

    def test_get_empty_product_list(self):
        """빈 상품 목록 조회 테스트"""

        # 기존 상품 모두 삭제
        Product.objects.all().delete()

        # API 요청
        url = reverse("product-list")
        response = self.client.get(url)

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 빈 배열 반환 확인
        response_data = response.data
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 0)


class ProductDetailAPITest(TestCase):
    """상품 상세 조회 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        
        # 기존 태그 생성
        self.tag1 = Tag.objects.create(name="Tag1")
        self.tag2 = Tag.objects.create(name="Tag2")
        
        # 테스트 상품 1 생성
        self.product1 = Product.objects.create(name="Product1")
        self.product1.tag_set.add(self.tag1)
        
        # 테스트 상품 1의 옵션 생성
        self.option1_1 = ProductOption.objects.create(
            product=self.product1, name="Option1_1", price=1000
        )
        self.option1_2 = ProductOption.objects.create(
            product=self.product1, name="Option1_2", price=2000
        )
        
        # 테스트 상품 2 생성 (옵션/태그 없음)
        self.product2 = Product.objects.create(name="Product2")

    def test_get_product_detail_success(self):
        """상품 상세 조회 성공 테스트"""

        # API 요청
        url = reverse("product-detail", kwargs={"pk": self.product1.pk})
        response = self.client.get(url)

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 구조 확인
        response_data = response.data
        self.assertIsInstance(response_data, dict)
        self.assertIn("pk", response_data)
        self.assertIn("name", response_data)
        self.assertIn("option_set", response_data)
        self.assertIn("tag_set", response_data)

        # 상품 데이터 확인
        self.assertEqual(response_data["name"], "Product1")
        self.assertEqual(response_data["pk"], self.product1.pk)

        # 옵션 데이터 확인
        self.assertEqual(len(response_data["option_set"]), 2)
        option_names = [opt["name"] for opt in response_data["option_set"]]
        self.assertIn("Option1_1", option_names)
        self.assertIn("Option1_2", option_names)

        # 태그 데이터 확인
        self.assertEqual(len(response_data["tag_set"]), 1)
        self.assertEqual(response_data["tag_set"][0]["name"], "Tag1")

    def test_get_product_detail_not_found(self):
        """존재하지 않는 상품 상세 조회 테스트"""

        # API 요청
        url = reverse("product-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        # 404 Not Found 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "상품을 찾을 수 없습니다.")

    def test_get_product_with_options_only(self):
        """옵션만 있는 상품 조회 테스트"""

        # 옵션만 있는 상품 생성
        product_with_options = Product.objects.create(name="ProductWithOptions")
        ProductOption.objects.create(
            product=product_with_options, name="OptionOnly", price=500
        )

        # API 요청
        url = reverse("product-detail", kwargs={"pk": product_with_options.pk})
        response = self.client.get(url)

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ProductWithOptions")
        self.assertEqual(len(response.data["option_set"]), 1)
        self.assertEqual(len(response.data["tag_set"]), 0)

    def test_get_product_with_tags_only(self):
        """태그만 있는 상품 조회 테스트"""

        # 태그만 있는 상품 생성
        product_with_tags = Product.objects.create(name="ProductWithTags")
        product_with_tags.tag_set.add(self.tag2)

        # API 요청
        url = reverse("product-detail", kwargs={"pk": product_with_tags.pk})
        response = self.client.get(url)

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "ProductWithTags")
        self.assertEqual(len(response.data["option_set"]), 0)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "Tag2")

    def test_get_product_without_options_and_tags(self):
        """옵션과 태그가 없는 상품 조회 테스트"""

        # API 요청
        url = reverse("product-detail", kwargs={"pk": self.product2.pk})
        response = self.client.get(url)

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Product2")
        self.assertEqual(len(response.data["option_set"]), 0)
        self.assertEqual(len(response.data["tag_set"]), 0)
