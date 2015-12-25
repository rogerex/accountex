from __future__ import unicode_literals
from django.contrib import admin
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
    def __unicode__(self): 
	return self.name

class AccountType(models.Model):
    CODE_TYPES = (
       ('ACTIVE', 'Active'),
       ('PASIVE', 'Pasive'),
       ('EXPENSE', 'Expense'),
       ('ACTIVE_EXPENSE', 'Active Expense'),
       ('CREDIT', 'Deposit'),
       ('PATRIMONY', 'Patrimony')       
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
    def __unicode__(self): 
	return self.name

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
    def __unicode__(self): 
	return self.title

class Seat(models.Model):
    id = models.AutoField(
        primary_key = True,
        db_column = 'seat_id', 
        editable = False
    )
    diary_book = models.ForeignKey(DiaryBook)
    code = models.CharField(
        max_length = 16L, 
        db_column = 'seat_code',
        unique = True,
        verbose_name = 'Code'
    )
    datetime = models.DateTimeField(
        db_column = 'seat_datetime',
        verbose_name = 'Datetime',
        default = datetime.datetime.today
    )
    debit = models.FloatField(
        db_column = 'seat_total_debit',
        verbose_name = 'Total Debit'
    )
    credit = models.FloatField(
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
    def __unicode__(self): 
	return self.code

class SeatDetail(models.Model):
    id = models.AutoField(
        primary_key = True,
        db_column = 'seat_detail_id', 
        editable = False
    )
    seat = models.ForeignKey(Seat)
    debitAccount = models.ForeignKey(
        Account,
        db_column = 'account_debit_id',
        verbose_name = 'Debit Account',
        related_name = '2'
    )
    creditAccount = models.ForeignKey(
        Account,
        db_column = 'account_credit_id',
        verbose_name = 'Credit Account',
        related_name = '1'
    )
    mount = models.FloatField(
        db_column = 'seat_detail_mount',
        verbose_name = 'Debit'
    )
    description = models.TextField(
    	db_column = 'seat_detail_description',
        verbose_name = 'Description'
    )
    class Meta:
        db_table = 'seat_detail'
    def __unicode__(self): 
        return ' '.join([self.seat.code, str(self.mount), '>>>Debit:', self.debitAccount.name, 'Credit:', self.creditAccount.name])

class SeatDetailInline(admin.TabularInline):
    model = SeatDetail
    extra = 3

class SeatAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Seat information', {'fields' : ['diary_book', 'code', 'datetime', 'debit', 'credit', 'description', 'status'], 'classes': ['collapse']})
    ]
    inlines = [SeatDetailInline]

class Vocabulary(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'vocabulary_id', 
        editable = False
    )
    name = models.CharField(
        max_length = 255L,
    	db_column = 'vocabulary_name',
        verbose_name = 'Name'
    )
    class Meta:
        db_table = 'vocabulary'
    def __unicode__(self): 
	return self.name

class Term(models.Model):
    id = models.AutoField(
        primary_key = True,
        db_column = 'term_id', 
        editable = False
    )
    vocabulary = models.ForeignKey(
        Vocabulary,
        db_column = 'vocabulary_id',
        verbose_name = 'Vocabulary'
    )
    name = models.CharField(
        max_length = 255L,
    	db_column = 'term_name',
        verbose_name = 'Name'
    )
    class Meta:
        db_table = 'term'
    def __unicode__(self): 
	return self.name

class TermInline(admin.TabularInline):
    model = Term
    extra = 1

class VocabularyAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [TermInline]


