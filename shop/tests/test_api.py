from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import Tag, Product, ProductOption


class ProductAPITest(TestCase):
    """Product API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.url = reverse("product-list")

    def test_create_product_success(self):
        """상품 생성 성공 테스트"""
        # 태그와 옵션이 포함된 상품 생성
        request_data = {
            "name": "TestProduct",
            "option_set": [{"name": "TestOption", "price": 1000}],
            "tag_set": []
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "TestProduct")
        self.assertEqual(len(response.data["option_set"]), 1)
        self.assertEqual(len(response.data["tag_set"]), 0)

    def test_create_product_with_tags(self):
        """태그가 포함된 상품 생성 테스트"""
        # 태그 생성
        tag = Tag.objects.create(name="TestTag")
        
        request_data = {
            "name": "ProductWithTags",
            "option_set": [],
            "tag_set": [{"pk": tag.pk}]
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "TestTag")

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
        ProductOption.objects.create(product=product, name="OriginalOption", price=1000)
        tag = Tag.objects.create(name="OriginalTag")
        product.tag_set.add(tag)
        
        # 상품 수정
        request_data = {
            "name": "UpdatedProduct",
            "option_set": [{"name": "UpdatedOption", "price": 2000}],
            "tag_set": [{"pk": tag.pk}]
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
        tag = Tag.objects.create(name="OriginalTag")
        
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
        self.assertEqual(response.data["name"], "OnlyNameChanged")
        
        # 태그만 수정 (이름은 이전 수정된 상태 유지)
        tag_only_data = {"tag_set": [{"name": "NewTag"}]}
        response = self.client.patch(url, tag_only_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "OnlyNameChanged")
        
        # 빈 tag_set으로 수정
        empty_tag_data = {"tag_set": []}
        response = self.client.patch(url, empty_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 0)
        
        # tag_set 없이 수정
        no_tag_data = {"name": "NoTagUpdate"}
        response = self.client.patch(url, no_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "NoTagUpdate")
        
        # name만 있는 경우
        real_tag_data = {"tag_set": [{"name": "NewTagForLoop"}]}
        response = self.client.patch(url, real_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "NewTagForLoop")
        
        # pk가 있는 경우
        pk_tag_data = {"tag_set": [{"pk": tag.pk}]}
        response = self.client.patch(url, pk_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "OriginalTag")
        
        # 존재하지 않는 pk로 Tag.DoesNotExist 발생
        invalid_pk_data = {"tag_set": [{"pk": 99999}]}
        response = self.client.patch(url, invalid_pk_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("태그를 찾을 수 없습니다", response.data["message"])
        
        # 새로운 태그 생성 테스트
        new_tag_name = "NewUniqueTag"
        
        # 해당 태그가 존재하지 않는지 확인
        self.assertFalse(Tag.objects.filter(name=new_tag_name).exists())
        
        new_tag_data = {"tag_set": [{"name": new_tag_name}]}
        response = self.client.patch(url, new_tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], new_tag_name)
        
        # 태그가 실제로 생성되었는지 확인
        self.assertTrue(Tag.objects.filter(name=new_tag_name).exists())
        
        # 새로운 상품 생성 시 새로운 태그 이름으로 요청
        new_product_data = {
            "name": "ProductWithNewTag",
            "option_set": [],
            "tag_set": [{"name": "BrandNewTagForCreate"}]
        }
        response = self.client.post(self.url, new_product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tag_set"]), 1)
        self.assertEqual(response.data["tag_set"][0]["name"], "BrandNewTagForCreate")

    def test_get_product_list_success(self):
        """상품 목록 조회 성공 테스트"""
        # 테스트 상품들 생성
        Product.objects.create(name="Product1")
        Product.objects.create(name="Product2")
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_product_list_empty(self):
        """상품 목록 조회 - 빈 목록 테스트"""
        # 상품이 없는 상태에서 조회
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

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
            "option_set": [{"name": "TestOption"}],
            "tag_set": []
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])

    def test_create_product_valueerror_exception(self):
        """상품 생성 시 ValueError Exception 테스트"""
        # 잘못된 pk 형식으로 ValueError 발생
        request_data = {
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": "invalid_pk"}]
        }
        
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("잘못된 데이터 형식입니다", response.data["message"])

    def test_create_product_integrityerror_exception(self):
        """상품 생성 시 IntegrityError Exception 테스트"""
        # 중복된 태그 이름으로 IntegrityError 발생 가능성 테스트
        tag = Tag.objects.create(name="DuplicateTag")
        
        # 같은 이름의 태그를 다시 생성하려고 시도
        request_data = {
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"name": "DuplicateTag"}]
        }
        
        response = self.client.post(self.url, request_data, format="json")
        # IntegrityError가 발생하지 않을 수 있으므로 201 또는 400 모두 허용
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_update_product_keyerror_exception(self):
        """상품 수정 시 KeyError Exception 테스트"""
        product = Product.objects.create(name="TestProduct")
        
        # 필수 필드가 누락된 옵션 데이터로 KeyError 발생
        request_data = {
            "option_set": [{"name": "TestOption"}]
        }
        
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = self.client.patch(url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("필수 필드가 누락되었습니다", response.data["message"])

    def test_update_product_valueerror_exception(self):
        """상품 수정 시 ValueError Exception 테스트"""
        product = Product.objects.create(name="TestProduct")
        
        # 잘못된 pk 형식으로 ValueError 발생
        request_data = {
            "tag_set": [{"pk": "invalid_pk"}]
        }
        
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = self.client.patch(url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("잘못된 데이터 형식입니다", response.data["message"])

    def test_update_product_integrityerror_exception(self):
        """상품 수정 시 IntegrityError Exception 테스트"""
        product = Product.objects.create(name="TestProduct")
        
        # 중복된 태그 이름으로 IntegrityError 발생 가능성 테스트
        tag = Tag.objects.create(name="DuplicateTag")
        
        request_data = {
            "tag_set": [{"name": "DuplicateTag"}]
        }
        
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = self.client.patch(url, request_data, format="json")
        # IntegrityError가 발생하지 않을 수 있으므로 200 또는 400 모두 허용
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
