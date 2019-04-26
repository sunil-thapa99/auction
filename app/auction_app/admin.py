from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.contrib.admin import helpers
from .models import Category, Product, Seller, Buyer, Event, Sales, Medium, ImageType, CommissionerBid, Image, UserCustomProfile
from django.utils.text import Truncator
from django.forms import ModelForm, ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.admin import UserAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	# Field name to be displayed. 
	list_display = ('category_name', 'slug', 'category_created', 'category_updated', )
	date_hierarchy = 'category_updated'
	# list_editable = ('category_name', )
	list_filter = ('category_created', 'category_updated')
	search_fields = ('category_name', 'slug', )
	# - represents negative order, last action at the top
	ordering = ('-category_updated', )

	list_per_page = 20
	prepopulated_fields = {'slug': ('category_name', )}

	def get_list_display(self, request):
		if request.user.is_superuser:
			return ('category_name', 'slug', 'category_created', 'category_updated')
		else:
			return ('category_name', 'slug', 'category_updated')

class ImageInline(admin.TabularInline):
	model = Image
	extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	inlines = (ImageInline,)

	def truncate_text(self):
	    text = "%s" % self.product_desc
	    return Truncator(text).chars(200)

	list_display = ('product_name', 'product_category', 'product_min_price', truncate_text, 'product_seller')
	date_hierarchy = 'product_updated'
	list_filter = ('product_category', 'product_created', 'product_updated', 'product_seller', 'product_date', 'product_by')
	search_fields = ('product_name',)
	suit_list_filter_horizontal = ('product_name', 'product_category', 'product_seller', )
	list_per_page = 20

	fieldsets = [
		(None, {
			'classes': ('suit-tab suit-tab-general',),
			'fields': ['product_name', 'product_category', 'product_min_price', ]
			}),
		('Description', {
			'classes': ('suit-tab suit-tab-general',),
			'description': 'Details about the product:',
			'fields': ['product_desc', 'product_by', 'product_date', 'product_medium_used', 'product_framed', 'product_height', 'product_length', 'product_image_type']
			}),
	]

	restricted_fieldset = [
		('Seller', {
			'classes': ('suit-tab suit-tab-general'),
			'description': 'Select Seller',
			'fields': ['product_seller']
			}),
		('Auction Date', {
			'classes': ('suit-tab suit-tab-general'),
			'description': 'Select Auction Date',
			'fields': ['product_auction_date']
			}),
		('Approve', {
			'classes': ('suit-tab suit-tab-general'),
			'description': 'Approve',
			'fields': ['approved']
			}),
	]

	def get_fieldsets(self, request, obj=None):
		if request.user.is_superuser:
			return self.fieldsets+self.restricted_fieldset
		else:
			return super(ProductAdmin, self).get_fieldsets(request, obj=obj)

	def save_model(self, request, obj, form, change):
		if not obj.product_seller:
			seller = Seller.objects.only('id').get(seller_username_id=request.user.id)
			obj.product_seller = seller

		if request.user.is_superuser:
			obj.approved = True

		super().save_model(request, obj, form, change)


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
	def name(self, obj):
		return obj.seller_username.first_name+' ' +obj.seller_username.last_name
	list_display = ('id', 'name', 'seller_username')
	list_per_page = 20
	def save_model(self, request, obj, form, change):
		obj.save()

@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
	def name(self, obj):
		return obj.buyer_username.first_name+' ' +obj.buyer_username.last_name
	list_display = ('id', 'name', 'buyer_username')
	list_per_page = 20
	def save_model(self, request, obj, form, change):
		obj.save()

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ('event_name', 'event_date', 'event_location', )
	list_filter = ('event_date', 'event_location', )
	search_fields = ('event_name', 'event_location', )
	suit_list_filter_horizontal = ('event_location', )
	list_per_page = 20

@admin.register(Sales)
class SalesAdmin(ImportExportModelAdmin):
	list_filter = ('sale_date',)
	list_per_page = 20

	change_list_template = 'admin/sales_analysis.html'

	def changelist_view(self, request, extra_context=None):
		if not request.user.is_superuser:
			extra_context = extra_context or {}
			extra_context['readonly'] = True
		response = super().changelist_view(request, extra_context=extra_context)
		try:
			query = response.context_data['cl'].queryset
		except (AttributeError, KeyError):
			return response
		total_sum = models.Sum('product_sold')
		metrics = {'total_product_sold': total_sum}
		data = {}
		data_list = []
		user_detail = User.objects.filter(username=request.user.username).values('id', 'username')[0]
		if user_detail['id'] != 1:
			seller_id = Seller.objects.filter(seller_username_id=user_detail['id']).values('id')[0]
			product_id = Product.objects.filter(product_seller_id=seller_id['id']).values('product_id', 'product_name', 'product_category')
			for product in product_id:
				result = Sales.objects.filter(product_sale_id=product['product_id']).values('id', 'product_sale', 'product_sold', 'sale_date').order_by('sale_date')[0]
				category = Category.objects.filter(id=product['product_category']).values('category_name')[0]
				commision = (0.1)*result['product_sold']
				for r in result:
					data = {
						'id': result['id'],
						'product_sale': product['product_name'],
						'product_sold': result['product_sold'],
						'sale_date': result['sale_date'],
						'category': category['category_name'],
						'commision': commision
					}
				data_list.append(data)
		else:
			result = query.values('product_sale', 'product_sold', 'sale_date').order_by('sale_date')
			for r in result:
				product = Product.objects.filter(product_id=r['product_sale']).values('product_category', 'product_name')[0]
				category = Category.objects.filter(id=product['product_category']).values('category_name')[0]
				commision = (0.1)*r['product_sold']
				data = {
					'product_sale': product['product_name'],
					'product_sold': r['product_sold'],
					'sale_date': r['sale_date'],
					'category': category['category_name'],
					'commision': commision
				}
				data_list.append(data)
		# map(lambda r: r.update({'check_box': helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME, r['pk'])}), data_list)
		response.context_data['product_summary'] = data_list
		response.context_data['total'] = dict(query.aggregate(**metrics))
		return response

@admin.register(Medium)
class MediumAdmin(admin.ModelAdmin):
	def name(self):
		return self.med_category.category_name
	list_display = (name, 'medium_used')
admin.site.register(ImageType)

class CommissionerBidAdminForm(ModelForm):
	class Meta:
		model = CommissionerBid
		fields = '__all__'

	def clean(self):
		if self.cleaned_data.get('min_bid_amount') > self.cleaned_data.get('max_bid_amount'):
			raise ValidationError("!!! Minimum bid amount is greater than Maxmimum bid amount !!!")

@admin.register(CommissionerBid)
class CommissionerBidAdmin(admin.ModelAdmin):
	form = CommissionerBidAdminForm
	def name(self, obj):
		return obj.buyer_User.buyer_username.first_name + ' ' + obj.buyer_User.buyer_username.last_name
	def product(self, obj):
		result = obj.product_name.product_name
		return result

	list_display = ('name', 'product', 'min_bid_amount', 'max_bid_amount', 'approved')
	
	fieldsets = [
		('Details', {
			'classes': ('suit-tab suit-tab-general',),
			'fields': ['product_name', ]
			}),
		('Amount', {
			'classes': ('suit-tab suit-tab-general',),
			'description': 'Details about the amount:',
			'fields': ['min_bid_amount', 'max_bid_amount']
			}),
	]

	restricted_fieldset = [
		('Approve', {
			'classes': ('suit-tab suit-tab-general'),
			'description': 'Approve',
			'fields': ['approved']
			}),
	]

	def get_fieldsets(self, request, obj=None):
		if request.user.is_superuser:
			return self.fieldsets+self.restricted_fieldset
		else:
			return super(CommissionerBidAdmin, self).get_fieldsets(request, obj=obj)

	def save_model(self, request, obj, form, change):
		if not obj.buyer_User:
			buyer = Buyer.objects.only('id').get(buyer_username_id=request.user.id)
			obj.buyer_User = buyer
		
		if request.user.is_superuser:
			obj.approved = True

		super().save_model(request, obj, form, change)

admin.site.site_header = 'Dashboard'
admin.site.site_title = 'Dashboard - Login'
admin.site.index_title = 'Welcome to the Dashboard'

class AdjUserAdmin(UserAdmin):
	UserAdmin.list_display += ('bank_account_number',)
	UserAdmin.fieldsets[1][1]['fields'] = ('title', 'first_name', 'last_name', 'email', 'address', 'tel_number', 'profile')
	UserAdmin.fieldsets += (
			('Bank Details', 
				{'fields': ('bank_account_number', 'bank_sort_code')}
			),
		)
	

class UserCustomProfileAdmin(admin.ModelAdmin):
	change_list_template = 'admin/profile.html'

	def changelist_view(self, request, extra_context=None):
		user_detail = User.objects.filter(id=request.user.id).values()[0]
		if not request.user.is_superuser:
			extra_context = extra_context or {}
			extra_context['readonly'] = True
		response = super().changelist_view(request, extra_context=extra_context)
		try:
			query = response.context_data['cl'].queryset
		except (AttributeError, KeyError):
			return response

		response.context_data['summary'] = {
			'user_name': user_detail['username'],
			'first_name': user_detail['first_name'],
			'last_name' : user_detail['last_name'],
			'title' : user_detail['title'],
			'last_login' : user_detail['last_login'],
			'email' : user_detail['email'],
			'date_joined' : user_detail['date_joined'],
			'bank_account_number' : user_detail['bank_account_number'],
			'bank_sort_code' : user_detail['bank_sort_code'],
			'address' : user_detail['address'],
			'tel_number' : user_detail['tel_number'],
			'profile' : user_detail['profile'],
		}
		return response
		
admin.site.register(UserCustomProfile, UserCustomProfileAdmin)

