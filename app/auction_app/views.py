from django.shortcuts import render
# Handle traffic from the site
from django.http import HttpResponse

from django.db.models import Q

from .models import Category, Medium, Event, Product, Seller, Image
from django.contrib.auth.models import User
from .filters import ProductFilter

def get_search_value():
	categories = Category.objects.all()
	medium = Medium.objects.all()
	event = Event.objects.all()

	value = {
		'categories': categories,
	}

	return value

# Create your views here.
def home(request):
	value = get_search_value()

	template_name = 'home_app/index.html'
	context ={
		'title': 'Home',
	}
	context.update(value)
	return render(request, template_name, context=context)

def search(request):
	value = get_search_value()
	template_name = 'home_app/search.html'
	data = Product.objects.all().values('id', 'product_name', 'product_by', 'product_date', 'product_desc')
	product_filter = ProductFilter(request.POST, queryset=data)
	product_filter = product_filter.qs
	for product in range(0, len(product_filter)):
		image = Image.objects.filter(product_image=product_filter[product]['id']).values('image_file')[0]
		image_list = {
			'image': image
		}
		product_filter[product].update(image_list)
	# print(product_filter)
	context= {
		'title': 'Search',
		'data': product_filter,
	}
	# print(request.POST)
	context.update(value)
	return render(request, template_name, context=context)

def load_medium(request):
	category_id = request.GET.get('category')
	medium = Medium.objects.filter(med_category=category_id).order_by('medium_used')
	return render(request, 'nav.html', {'medium': medium})

def product(request, value):
	search_value = get_search_value()
	template_name = 'home_app/product.html'
	final_data = []
	instance_data = {}
	# query = request.GET.get('value')
	search_result = Product.objects.filter(id=value).values().annotate()
	for result in search_result:
		category = Category.objects.filter(id=result['product_category_id']).values('category_name')[0]
		seller = Seller.objects.filter(id=result['product_seller_id']).values('seller_username_id')[0]
		seller = User.objects.filter(id=seller['seller_username_id']).values('first_name', 'last_name')[0]
		image = Image.objects.filter(product_image=result['id']).values('image_file')
		instance_data = {
					'product_name': result['product_name'],
					'product_category': category,
					'product_desc': result['product_desc'],
					'product_image': image,
					'product_min_price': result['product_min_price'],
					'artist': result['product_by'],
					'product_date': result['product_date'],
					'product_seller': seller,
					'product_height': result['product_height'],
					'product_length': result['product_length'],
				}
		if result['product_medium_used_id']:
			medium = Medium.objects.filter(id=result['product_medium_used_id']).values('medium_used')[0]
			instance_data.update({'product_medium_used': medium})

		if result['product_auction_date_id']:
			event = Event.objects.filter(id=result['product_auction_date_id']).values('event_name', 'event_date', 'event_location')[0]
			instance_data.update({'product_auction_date': event})

		if result['product_framed']:
			instance_data.update({'product_framed': result['product_framed']})

		if 'product_image_type' in result:
			instance_data.update({'product_image_type': result['product_image_type']})
		final_data.append(instance_data)
	context= {
		'title': 'Search',
		'data': final_data,
	}
	context.update(search_value)
	return render(request, template_name, context=context)