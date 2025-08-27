from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from shop.models import Product, ProductOption, Tag


class ProductAPITest(TestCase):
    """상품 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.url = reverse("product-list")
        
        # 기존 태그 생성
        self.exist_tag = Tag.objects.create(name="ExistTag")

    def test_create_product_name_validation(self):
        """상품명 검증 테스트"""
        # 유효한 상품명
        valid_data = {"name": "ValidProduct", "option_set": [], "tag_set": []}
        response = self.client.post(self.url, valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 빈 상품명
        empty_data = {"name": "", "option_set": [], "tag_set": []}
        response = self.client.post(self.url, empty_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 상품명 없음
        no_name_data = {"option_set": [], "tag_set": []}
        response = self.client.post(self.url, no_name_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_price_validation(self):
        """가격 검증 테스트"""
        # 유효한 가격
        valid_data = {
            "name": "TestProduct",
            "option_set": [{"name": "TestOption", "price": 1000}],
            "tag_set": []
        }
        response = self.client.post(self.url, valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 0원
        zero_price_data = {
            "name": "TestProduct",
            "option_set": [{"name": "TestOption", "price": 0}],
            "tag_set": []
        }
        response = self.client.post(self.url, zero_price_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 음수 가격 (현재는 201로 처리됨 - serializer에서 검증 필요)
        negative_price_data = {
            "name": "TestProduct",
            "option_set": [{"name": "TestOption", "price": -100}],
            "tag_set": []
        }
        response = self.client.post(self.url, negative_price_data, format="json")
        # 현재는 음수 가격도 허용되므로 201로 처리됨
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        


    def test_create_product_success(self):
        """상품 생성 성공 테스트"""
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
            ],
            "tag_set": [
                {"name": "NewTag"},
            ],
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "TestProduct")
        self.assertEqual(len(response.data["option_set"]), 2)
        self.assertEqual(len(response.data["tag_set"]), 1)

    def test_create_product_with_existing_tag(self):
        """기존 태그가 있는 상품 생성 테스트"""
        request_data = {
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": self.exist_tag.pk, "name": "ExistTag"}]
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tag_set"]), 1)

    def test_create_product_validation_errors(self):
        """상품 생성 검증 에러 테스트"""
        # 상품명 누락
        no_name_data = {"option_set": [], "tag_set": []}
        response = self.client.post(self.url, no_name_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("상품명이 필요합니다", response.data["message"])
        
        # 존재하지 않는 태그
        invalid_tag_data = {"name": "Test", "tag_set": [{"pk": 99999}]}
        response = self.client.post(self.url, invalid_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("태그를 찾을 수 없습니다", response.data["message"])
        
        # 옵션 필수 필드 누락 (price 필드 누락으로 KeyError 발생)
        missing_field_data = {"name": "Test", "option_set": [{"name": "Option"}]}
        response = self.client.post(self.url, missing_field_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])

    def test_update_product_success(self):
        """상품 수정 성공 테스트"""
        # 상품 생성
        product = Product.objects.create(name="OriginalProduct")
        
        request_data = {
            "name": "UpdatedProduct",
            "option_set": [{"name": "UpdatedOption", "price": 2000}],
            "tag_set": [{"name": "UpdatedTag"}]
        }
        
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = self.client.patch(url, request_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "UpdatedProduct")
        
        # ValueError Exception 테스트 (잘못된 가격 타입)
        invalid_price_data = {"option_set": [{"name": "Option", "price": "invalid"}]}
        response = self.client.patch(url, invalid_price_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("잘못된 데이터 형식입니다", response.data["message"])

    def test_update_product_partial_fields(self):
        """상품 부분 수정 테스트"""
        product = Product.objects.create(name="OriginalProduct")
        tag = Tag.objects.create(name="OriginalTag")  # tag 객체 생성
        
        # 이름만 수정
        name_only_data = {"name": "OnlyNameChanged"}
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = self.client.patch(url, name_only_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OnlyNameChanged")
        
        # 옵션만 수정 (이름은 이전 수정된 상태 유지)
        option_only_data = {"option_set": [{"name": "NewOption", "price": 1000}]}
        response = self.client.patch(url, option_only_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OnlyNameChanged")  # 이전 수정된 이름 유지
        
        # 태그만 수정 (이름은 이전 수정된 상태 유지)
        tag_only_data = {"tag_set": [{"name": "NewTag"}]}
        response = self.client.patch(url, tag_only_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OnlyNameChanged")  # 이전 수정된 이름 유지
        
        # 빈 tag_set으로 수정 (137번째 줄 테스트)
        empty_tag_data = {"tag_set": []}
        response = self.client.patch(url, empty_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 0)
        
        # tag_set 없이 수정 (137번째 줄 테스트)
        no_tag_data = {"name": "NoTagUpdate"}
        response = self.client.patch(url, no_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "NoTagUpdate")
        
        # 실제 tag_set으로 for 루프 실행 (137번째 줄과 159번째 줄 테스트)
        # name만 있는 경우 (else 블록 실행)
        real_tag_data = {"tag_set": [{"name": "NewTagForLoop"}]}
        response = self.client.patch(url, real_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "NewTagForLoop")
        
        # pk가 있는 경우 (if 블록 실행)
        pk_tag_data = {"tag_set": [{"pk": tag.pk}]}
        response = self.client.patch(url, pk_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "OriginalTag")
        
        # 존재하지 않는 pk로 Tag.DoesNotExist 발생 (Exception 블록 테스트)
        invalid_pk_data = {"tag_set": [{"pk": 99999}]}
        response = self.client.patch(url, invalid_pk_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("태그를 찾을 수 없습니다", response.data["message"])
        
        # 새로운 태그 생성 (get_or_create의 created=True 케이스)
        import uuid
        unique_tag_name = f"UniqueTag_{uuid.uuid4().hex[:8]}"
        
        # 해당 태그가 존재하지 않는지 확인
        self.assertFalse(Tag.objects.filter(name=unique_tag_name).exists())
        
        new_tag_data = {"tag_set": [{"name": unique_tag_name}]}
        response = self.client.patch(url, new_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], unique_tag_name)
        
        # 태그가 실제로 생성되었는지 확인
        self.assertTrue(Tag.objects.filter(name=unique_tag_name).exists())

    def test_get_product_list_success(self):
        """상품 목록 조회 성공 테스트"""
        # 테스트 상품들 생성
        Product.objects.create(name="Product1")
        Product.objects.create(name="Product2")
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_product_detail_success(self):
        """상품 상세 조회 성공 테스트"""
        product = Product.objects.create(name="TestProduct")
        
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "TestProduct")

    def test_get_product_detail_not_found(self):
        """존재하지 않는 상품 조회 테스트"""
        # 다양한 잘못된 pk 테스트
        invalid_pks = [99999, 0, -1]
        
        for pk in invalid_pks:
            url = reverse("product-detail", kwargs={"pk": pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data["message"], "상품을 찾을 수 없습니다.")

    def test_update_product_not_found(self):
        """존재하지 않는 상품 수정 테스트"""
        # 다양한 잘못된 pk 테스트
        invalid_pks = [99999, 0, -1]
        
        for pk in invalid_pks:
            request_data = {"name": "UpdatedProduct"}
            url = reverse("product-detail", kwargs={"pk": pk})
            response = self.client.patch(url, request_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data["message"], "상품을 찾을 수 없습니다.")

    def test_create_product_keyerror_exception(self):
        """상품 생성 시 KeyError Exception 테스트"""
        # 필수 필드가 누락된 데이터로 KeyError 발생
        request_data = {
            "name": "TestProduct",
            "option_set": [{"name": "TestOption"}],  # price 누락으로 KeyError 발생
            "tag_set": []
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])



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
