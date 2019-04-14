from django.db import models
from django.utils.text import slugify

from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator
from django.conf import settings

from django import forms
from datetime import datetime
from time import time

def storeImage(instance, filename):
	return"auction_media/image_{0}_{1}".format(str(time()),filename)

def eventImage(instance, filename):
	return"event/image_{0}_{1}".format(str(time()),filename)	

class Category(models.Model):
	category_name = models.CharField(max_length=50, unique=True, blank=False, null=False, \
		help_text='New category must be unique')
	slug = models.SlugField(blank=True, unique=True, help_text='You don\'t need to enter this field')
	# Takes date and time from the system in the database and it can't be updated 
	category_created = models.DateTimeField(auto_now_add=True)
	# On each update time can be changed
	category_updated = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.category_name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.category_name		
	class Meta:
		verbose_name_plural = 'Categories'
			

class Seller(models.Model):
	seller_username = models.ForeignKey(User, on_delete=models.CASCADE,limit_choices_to={'groups__name': 'Seller'})

	seller_created = models.DateTimeField(auto_now_add=True)
	seller_updated = models.DateTimeField(auto_now=True)

	is_active = models.BooleanField(default=False)
	def __str__(self):
		return self.seller_username.first_name + ' ' + self.seller_username.last_name

class Buyer(models.Model):
	buyer_username = models.ForeignKey(User, on_delete=models.CASCADE,limit_choices_to={'groups__name': 'Buyer'})

	buyer_created = models.DateTimeField(auto_now_add=True)
	buyer_updated = models.DateTimeField(auto_now=True)

	is_active = models.BooleanField(default=False)

	def __str__(self):
		return self.buyer_username.first_name + ' ' + self.buyer_username.last_name

class Event(models.Model):
	event_name = models.CharField(max_length=255, blank=False, null=False)
	slug = models.SlugField(blank=True)
	event_desc = models.TextField(blank=True, null=False, default='')
	event_date = models.DateField(blank=False, null=False)
	event_location = models.CharField(max_length=200, blank=False, null=False)
	thumbnail = models.ImageField(upload_to=eventImage, blank=True, null=False)

	def __unicode__(self):
		return self.event_name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.event_name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.event_name

	class Meta:
		ordering = ('event_date', )
		verbose_name_plural = 'Events'

	def get_absolute_image_url(self):
		return os.path.join(settings.MEDIA_URL, self.thumbnail.url)

class Medium(models.Model):
	medium_used = models.CharField(max_length=250, blank=False,)
	med_category = models.ForeignKey(Category, on_delete=models.CASCADE,)

	def __str__(self):
		return self.medium_used

	class Meta:
		verbose_name_plural = 'Medium Used'

class ImageType(models.Model):
	type_image = models.CharField(max_length=10, blank=False)


class Product(models.Model):
	product_name = models.CharField(max_length=250,blank=False, null=False)
	slug = models.SlugField(blank=True, help_text='You don\'t need to enter this field')
	product_category = models.ForeignKey(Category, on_delete=models.CASCADE,)

	product_desc = models.TextField(blank=False, null=False,)
	# product_image = models.FileField('File', upload_to=storeImage)
	product_min_price = models.FloatField(null=False, blank=False)

	product_by = models.CharField(verbose_name='Artist', max_length=250, blank=False, null=False)
	product_date = models.DateField(verbose_name='Created Date', blank=False, null=False)

	product_seller = models.ForeignKey(Seller, on_delete=models.CASCADE,)
	product_auction_date = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)

	product_medium_used = models.ForeignKey(Medium, on_delete=models.CASCADE, blank=True, null=True)
	product_framed = models.BooleanField(default=False)
	product_height = models.FloatField(blank=False, default='')
	product_length = models.FloatField(blank=False, default='')
	product_image_type = models.ForeignKey(ImageType, on_delete=models.CASCADE, blank=True, null=True)

	product_created = models.DateTimeField(auto_now_add=True)
	product_updated = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.product_name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.product_name


class Image(models.Model):
	image_file = models.FileField('File', upload_to=storeImage)
	product_image = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)

	def __str__(self):
	    return self.filename

	def get_absolute_image_url(self):
		return os.path.join(settings.MEDIA_URL, self.product_image.url)

	@property
	def filename(self):
		return self.image_file.name.rsplit('/', 1)[-1]

class Sales(models.Model):
	product_sale = models.ForeignKey(Product, on_delete=models.CASCADE)
	product_sold = models.FloatField(null=False, blank=True)
	sale_date = models.DateField(blank=True, null=True, help_text='Format: YYYY-MM-DD', default=datetime.now)
	sales_created = models.DateTimeField(auto_now_add=True)
	sales_updated = models.DateTimeField(auto_now=True)
	def save(self, *args, **kwargs):
		if not self.product_sold:
			self.product_sold = self.product_sale.product_min_price
		super().save(*args, **kwargs)

	class Meta:
		ordering = ('sale_date', )
		verbose_name_plural = 'Sales'

class CommissionerBid(models.Model):
	product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
	buyer_User = models.ForeignKey(Buyer, on_delete=models.CASCADE)

	min_bid_amount = models.FloatField(blank=False, null=False)
	max_bid_amount = models.FloatField(blank=False, null=False)
	approved = models.BooleanField(default=False)
	bid_created = models.DateTimeField(auto_now_add=True)
	bid_updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('bid_updated',)
		verbose_name_plural = 'Apply Commissioner Bid'
