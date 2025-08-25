from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.response import Response

from shop.models import Product, ProductOption, Tag
from shop.serializers import ProductCreateSerializer


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    http_method_names = ['get', 'post', 'patch']  # GET, POST, PATCH 허용

    # 상품 목록 조회 API
    def list(self, request, *args, **kwargs):
        try:
            # 데이터 호출
            products = (
                Product.objects.select_related()
                .prefetch_related("option_set", "tag_set")
                .all()
            )
            
            # 응답 데이터 생성
            serializer = ProductCreateSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"message": f"서버 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 상품 상세 조회 API
    def retrieve(self, request, *args, **kwargs):
        try:
            # 데이터 호출
            pk = kwargs.get('pk')
            product = (
                Product.objects.select_related()
                .prefetch_related("option_set", "tag_set")
                .get(pk=pk)
            )
            
            # 응답 데이터 생성
            serializer = ProductCreateSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            return Response({"message": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"서버 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        except Tag.DoesNotExist:
            return Response(
                {"message": "태그를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError as e:
            return Response(
                {"message": f"필수 필드가 누락되었습니다: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"message": f"잘못된 데이터 형식입니다: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": f"서버 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # 상품 수정 API
    def update(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk")
            product = Product.objects.get(pk=pk)

            # 트랜잭션으로 데이터 수정
            with transaction.atomic():
                # 상품명 부분 수정 (요청에 있을 때만)
                if "name" in request.data:
                    product.name = request.data["name"]
                    product.save()

                # 옵션 부분 수정 (요청에 있을 때만)
                if "option_set" in request.data:
                    # 기존 옵션 모두 제거
                    product.option_set.all().delete()
                    
                    # 새로운 옵션 생성
                    for option_data in request.data["option_set"]:
                        ProductOption.objects.create(
                            product=product,
                            name=option_data["name"],
                            price=option_data["price"],
                        )

                # 태그 부분 수정 (요청에 있을 때만)
                if "tag_set" in request.data:
                    # 기존 태그 연결 모두 제거
                    product.tag_set.clear()
                    
                    # 새로운 태그 처리
                    for tag_data in request.data["tag_set"]:
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
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response(
                {"message": "상품을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Tag.DoesNotExist:
            return Response(
                {"message": "태그를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError as e:
            return Response(
                {"message": f"필수 필드가 누락되었습니다: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"message": f"잘못된 데이터 형식입니다: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": f"서버 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
