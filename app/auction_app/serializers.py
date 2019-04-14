class ProductSerializer(serializers.ModelSerializer):

    image_url = serializers.URLField(source='get_absolute_image_url', read_only=True, many=True)

    class Meta:
        model = Product
        fields = ('product_name', 'product_image')
