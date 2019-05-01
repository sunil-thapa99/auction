from django.conf.urls import url, include
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django_filters.views import FilterView
from .filters import ProductFilter

urlpatterns = [
    url(r'^medium/', views.load_medium, name="medium"),
    url(r'^search/$', views.search, name="search"),
    url(r'^products/', views.products, name="products"),
    url(r'^events/', views.events, name="events"),
    url(r'^product/(?P<value>\d+)/$', views.product, name="product"),
    url(r'^event/(?P<value>\d+)/$', views.event, name="event"),
    url(r'^notifications/', include('notify.urls', 'notifications')),
    url(r'^catalogue/(?P<value>\d+)/$', views.catalogue, name="catalogue"),
    url(r'^$', views.home, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)