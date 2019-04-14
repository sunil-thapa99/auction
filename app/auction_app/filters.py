from .models import Product
import django_filters

class ProductFilter(django_filters.FilterSet):
	product_name = django_filters.CharFilter(lookup_expr='icontains')
	product_by = django_filters.CharFilter(lookup_expr='icontains')
	
	class Meta:
		model = Product
		fields = ['product_name', 'product_category', 'product_medium_used', 'product_by', 'product_date']
