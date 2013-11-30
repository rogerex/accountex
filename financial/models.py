from __future__ import unicode_literals
from django.db import models
import datetime

# Create your models here.
STATUS = (
   (1, 'Active'),
   (2, 'Inactive'),
)

class Account(models.Model):
    id = models.IntegerField(
        db_column = 'account_id',
        editable = False,
        primary_key = True
    )
    account_type = models.ForeignKey('AccountType')
    code = models.CharField(
        db_column = 'account_code', 
        max_length = 16L
    )
    name = models.CharField(
        db_column = 'account_name', 
        max_length = 255L
    )
    description = models.TextField(
        db_column = 'account_description'
    )
    datetime = models.DateTimeField(
        db_column = 'account_datetime',
        default = datetime.datetime.today
    )
    class Meta:
        db_table = 'account'

class AccountType(models.Model):
    CODE_TYPES = (
       ('ACTIVE', 'Active'),
       ('PASIVE', 'Pasive'),
       ('PATRIMONY', 'Patrimony'),
    )
    id = models.IntegerField(
        db_column = 'account_type_id', 
        editable = False,
        primary_key = True
    )
    typeCodeId = models.CharField(
        db_column = 'account_type_code', 
        verbose_name = 'Code Type', 
        max_length = 16L, 
        help_text = 'Selecciona el tipo de codigo de cuenta',
        choices = CODE_TYPES
    )
    name = models.CharField(
        db_column = 'account_type_name', 
        verbose_name = 'Name', 
        max_length = 255L
    )
    description = models.TextField(
        db_column = 'account_type_description', 
        verbose_name = 'Description'
    )
    class Meta:
        db_table = 'account_type'

class Balance(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'balance_id', 
        editable = False,
    )
    datetime = models.DateTimeField(
        db_column = 'balance_datetime',
        verbose_name = 'Date',
        default = datetime.datetime.today
    )
    debit = models.DecimalField(
        max_digits = 12, 
        decimal_places = 10,
        db_column = 'balance_debit',
        verbose_name = 'Debit'
    )
    credit = models.DecimalField(
        max_digits = 12,
        decimal_places = 10,
        db_column = 'balance_credit',
        verbose_name = 'Credit'
    )
    class Meta:
        db_table = 'balance'

class BalanceDetail(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'balance_detail_id', 
        editable = False,
    )
    account = models.ForeignKey(Account)
    balance = models.ForeignKey(Balance)
    debit = models.DecimalField(
        max_digits = 12,
        decimal_places = 10,
        db_column = 'balance_detail_debit',
        verbose_name = 'Credit'
    )
    credit = models.DecimalField(
        max_digits = 12,
        decimal_places = 10,
        db_column = 'balance_detail_credit',
        verbose_name = 'Credit'
    )
    class Meta:
        db_table = 'balance_detail'

class DiaryBook(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'diary_book_id', 
        editable = False,
    )
    title = models.CharField(
        max_length = 255L,
        db_column = 'diary_book_title',
        verbose_name = 'Title'
    )
    init = models.DateTimeField(
        db_column = 'diary_book_init',
        verbose_name = 'Init',
        default = datetime.datetime.today
    )
    final = models.DateTimeField(
        db_column = 'diary_book_final',
        verbose_name = 'Final',
        default = datetime.datetime.today
    )
    status = models.IntegerField(
        db_column = 'diary_book_status',
        verbose_name = 'Status',
        choices = STATUS
    )
    class Meta:
        db_table = 'diary_book'

class Seat(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'seat_id', 
        editable = False
    )
    diary_book = models.ForeignKey(DiaryBook)
    code = models.CharField(
        max_length = 16L, 
        db_column = 'seat_code',
        verbose_name = 'Code'
    )
    datetime = models.DateTimeField(
        db_column = 'seat_datetime',
        verbose_name = 'Datetime',
        default = datetime.datetime.today
    )
    debit = models.DecimalField(
        max_digits = 12,
        decimal_places = 10,
        db_column = 'seat_total_debit',
        verbose_name = 'Total Debit'
    )
    credit = models.DecimalField(
        max_digits = 12, 
        decimal_places = 10,
        db_column = 'seat_total_credit',
        verbose_name = 'Total Credit'
    )
    description = models.TextField(
    	db_column = 'seat_description',
        verbose_name = 'Description'
    )
    status = models.IntegerField(
        db_column = 'seat_status',
        verbose_name = 'Status',
        choices = STATUS
    )
    class Meta:
        db_table = 'seat'

class SeatDetail(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'seat_detail_id', 
        editable = False
    )
    seat = models.ForeignKey(Seat)
    account = models.ForeignKey(Account)
    debit = models.DecimalField(
        max_digits = 12, 
        decimal_places = 10,
        db_column = 'seat_detail_debit',
        verbose_name = 'Debit'
    )
    credit = models.DecimalField(
        max_digits = 12, 
        decimal_places = 10,
        db_column = 'seat_detail_credit',
        verbose_name = 'Credit'
    )
    class Meta:
        db_table = 'seat_detail'

