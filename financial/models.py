from __future__ import unicode_literals
from django.contrib import admin
from django.db import models
from django.utils.html import escape, format_html
import datetime
from django import forms
from financial.seat_initial_default import INITIAL_SEAT_DETAIL

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
    account_type = models.ForeignKey('AccountType', on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    code = models.CharField(
        db_column = 'account_code', 
        max_length = 16
    )
    name = models.CharField(
        db_column = 'account_name', 
        max_length = 255
    )
    description = models.TextField(
        db_column = 'account_description'
    )
    datetime = models.DateTimeField(
        db_column = 'account_datetime',
        default = datetime.datetime.today
    )
    field_order = ['account_name', ]
    class Meta:
        db_table = 'account'
        ordering = ('name',)
    def report(self):
        return format_html('<a href="./{0}/report">Report</a>', str(self.id))
    def __str__(self):
        return self.name

class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_type', 'code', 'name', 'currency', 'datetime', 'report']

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
        max_length = 16,
        help_text = 'Selecciona el tipo de codigo de cuenta',
        choices = CODE_TYPES
    )
    name = models.CharField(
        db_column = 'account_type_name', 
        verbose_name = 'Name', 
        max_length = 255
    )
    description = models.TextField(
        db_column = 'account_type_description', 
        verbose_name = 'Description'
    )

    def report(self):
        return format_html('<a href="../account-type/{0}/report">Report</a>', str(self.id))
    class Meta:
        db_table = 'account_type'
    def __str__(self): 
        return self.name

class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'report']

class Currency(models.Model):
    id = models.AutoField(
        db_column = 'currency_id', 
        editable = False,
        primary_key = True
    )
    name = models.CharField(
        db_column = 'currency_name',
        verbose_name = 'Name',
        max_length = 21,
        default = 'XYZ Currency'
    )
    code = models.CharField(
        db_column = 'currency_code',
        verbose_name = 'Code',
        max_length = 11,
    )
    symbol = models.CharField(
        db_column = 'currency_symbol',
        verbose_name = 'Symbol',
        max_length = 11,
    )
    class Meta:
        db_table = 'currency'
    def __str__(self): 
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
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
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
        max_length = 255,
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
    def __str__(self): 
        return self.title

class Seat(models.Model):
    id = models.AutoField(
        primary_key = True,
        db_column = 'seat_id', 
        editable = False
    )
    diary_book = models.ForeignKey(DiaryBook, on_delete=models.CASCADE, limit_choices_to={'status': True})
    code = models.CharField(
        max_length = 16,
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
    def report(self):
        return format_html('<a href="./{0}/report">Report</a>', str(self.id))
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
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    debitAccount = models.ForeignKey(
        Account,
        db_column = 'account_debit_id',
        verbose_name = 'Debit Account',
        related_name = 'debitAccount',
        on_delete = models.CASCADE,
    )
    creditAccount = models.ForeignKey(
        Account,
        db_column = 'account_credit_id',
        verbose_name = 'Credit Account',
        related_name = 'creditAccount',
        on_delete = models.CASCADE,
    )
    mount = models.FloatField(
        db_column = 'seat_detail_mount',
        verbose_name = 'Mount'
    )
    description = models.TextField(
        db_column = 'seat_detail_description',
        verbose_name = 'Description'
    )
    class Meta:
        db_table = 'seat_detail'
    def __unicode__(self): 
        return ' '.join([self.seat.code, str(self.mount), '>>>Debit:', self.debitAccount.name, 'Credit:', self.creditAccount.name])

queryParamForDefault = 'initial'

class SeatDetailInlineFormSet(forms.models.BaseInlineFormSet):
    model = SeatDetail
    def __init__(self, *args, **kwargs):
        super(SeatDetailInlineFormSet, self).__init__(*args, **kwargs)
        if self.request.GET.get(queryParamForDefault, None):
            self.initial=INITIAL_SEAT_DETAIL

class SeatDetailInline(admin.TabularInline):
    model = SeatDetail
    extra = 3
    formset = SeatDetailInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(SeatDetailInline, self).get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

    def get_extra(self, request, obj=None, **kwargs):
        extra = super(SeatDetailInline, self).get_extra(request, obj, **kwargs)
        something = request.GET.get(queryParamForDefault, None)
        if something:
            extra = INITIAL_SEAT_DETAIL.__len__()
        return extra

class SeatAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Seat information', {'fields' : ['diary_book', 'code', 'datetime', 'debit', 'credit', 'description', 'status'], 'classes': ['collapse']})
    ]
    inlines = [SeatDetailInline]
    list_display = ['code', 'datetime', 'debit', 'credit', 'report', 'status']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.GET.get(queryParamForDefault, None): # Only for initial
            form.base_fields['diary_book'].initial = 13
            form.base_fields['code'].initial = datetime.datetime.today().strftime('%Y %m 00')

            debit = 0
            for item in INITIAL_SEAT_DETAIL:
                if item['description'].startswith('Gastos -'):
                    debit += item['mount']

            credit = 0
            for item in INITIAL_SEAT_DETAIL:
                if item['description'].startswith('% B') or item['description'].startswith('Ingresos:'):
                    credit += item['mount']

            creditUSD = 0
            for item in INITIAL_SEAT_DETAIL:
                if item['description'].startswith('$ %'):
                    creditUSD += item['mount']

            form.base_fields['debit'].initial = debit
            form.base_fields['credit'].initial = credit

            line1 = 'Gastos Estimados - Bs {}'.format(debit)
            line2 = 'Ingresos Estimados - Bs {}'.format(credit)
            line3 = 'Ingresos Estimados - $us {}'.format(creditUSD)
            form.base_fields['description'].initial = line1 + '\n' + line2 + '\n' + line3

            form.base_fields['status'].initial = 1

        return form

class Vocabulary(models.Model):
    id = models.IntegerField(
        primary_key = True,
        db_column = 'vocabulary_id', 
        editable = False
    )
    name = models.CharField(
        max_length = 255,
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
        verbose_name = 'Vocabulary',
        on_delete = models.CASCADE
    )
    name = models.CharField(
        max_length = 255,
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


