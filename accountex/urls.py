from django.urls import include, re_path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'accountex.views.home', name='home'),
    # url(r'^accountex/', include('accountex.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    re_path(r'^admin/', include('financial.urls')),
    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls),
]
