from django.urls import re_path
from financial import views
from .reports.accountType import account_type_report
from .reports.seat import seat_report
from .reports.account import account_report
from .reports.patrimony import execute_patrimony_raw_sql
from .dashboard.performance import performance_widget

urlpatterns = [
    # ex: /seat/5/report/
    re_path(r'^financial/seat/(?P<id>\d+)/report/$', seat_report, name='seat_report'),
    # ex: /account/5/report/
    re_path(r'^financial/account/(?P<id>\d+)/report/$', account_report, name='account_report'),
    # ex: /account-type/5/report/
    re_path(r'^financial/account-type/(?P<id>\d+)/report/$', account_type_report, name='account_type_report'),
    re_path(r'^financial/patrimony/$', execute_patrimony_raw_sql, name='patrimony_report'),
    re_path(r'^financial/dashboard/performance/$', performance_widget, name='performance_widget'),
]
