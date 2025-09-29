from django.urls import re_path
from financial import views
from .reports.accountType import account_type_report

urlpatterns = [
    # ex: /seat/5/report/
    re_path(r'^financial/seat/(?P<id>\d+)/report/$', views.seat_report, name='seat_report'),
    # ex: /account/5/report/
    re_path(r'^financial/account/(?P<id>\d+)/report/$', views.account_report, name='account_report'),
    # ex: /account-type/5/report/
    re_path(r'^financial/account-type/(?P<id>\d+)/report/$', account_type_report, name='account_type_report'),
]
