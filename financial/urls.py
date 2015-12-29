from django.conf.urls import patterns, url
from financial import views

urlpatterns = patterns('',
    # ex: /seat/5/report/
    url(r'^financial/seat/(?P<id>\d+)/report/$', views.seat_report, name='seat_report'),
    # ex: /account/5/report/
    url(r'^financial/account/(?P<id>\d+)/report/$', views.account_report, name='account_report')
)
