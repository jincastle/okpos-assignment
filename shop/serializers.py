from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from shop.models import Product, ProductOption, Tag


class ProductOptionSerializer(WritableNestedModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['pk', 'name', 'price']


class TagSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Tag
        fields = ['pk', 'name']


class ProductCreateSerializer(WritableNestedModelSerializer):
    option_set = ProductOptionSerializer(many=True)
    tag_set = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = ['pk', 'name', 'option_set', 'tag_set']
