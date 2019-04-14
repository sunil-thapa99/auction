from django.conf.urls import url
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django_filters.views import FilterView
from .filters import ProductFilter

urlpatterns = [
    url(r'^medium/', views.load_medium, name="medium"),
    url(r'^search/$', views.search, name="search"),
    url(r'^product/(?P<value>\d+)/$', views.product, name="product"),
    url(r'^$', views.home, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)