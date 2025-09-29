from __future__ import unicode_literals
from django.contrib import admin
from django.db import models
from django.utils.html import escape, format_html
import datetime
from django import forms

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
    list_display = ['id', 'account_type', 'code', 'name', 'datetime', 'report']

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

INITIAL_SEAT_DETAIL = [
    ### Fondo de emergencia (Intereses ganados)
    {'debitAccount': 205, 'creditAccount': 148, 'description': '% Aave Coinbase Wallet (Delete)', 'mount': 4, },
    {'debitAccount': 155, 'creditAccount': 148, 'description': '% Staking Coinbase Exchange (Delete)', 'mount': 4, },
    {'debitAccount': 146, 'creditAccount': 148, 'description': '% Staking Kraken Exchange (Delete)', 'mount': 4, },

    ### Fondo de ahorros para alguna de mis objetos de consumo (Intereses ganados)
    {'debitAccount': 145, 'creditAccount': 148, 'description': '% Defi Blend Meru Wallet (Delete)', 'mount': 4, },

    ### Fondo de IT (Intereses ganados), yo creo en un futuro me voy a comprar una casa
    #{'debitAccount': 157, 'creditAccount': 148, 'description': '% Aave Coinbase Wallet (Delete)', 'mount': 4, },
    #{'debitAccount': 154, 'creditAccount': 148, 'description': '% Defi Nebeus Wallet (Delete)', 'mount': 4, },
    #{'debitAccount': 153, 'creditAccount': 148, 'description': '% Staking Nexo Exchange (Delete)', 'mount': 0, },

    ### Bancos (Intereses ganados)
    {'debitAccount': 206, 'creditAccount': 26, 'description': '% BB (Delete)', 'mount': 1, },
    {'debitAccount': 124, 'creditAccount': 26, 'description': '% BE (Delete)', 'mount': 1, },
    {'debitAccount': 156, 'creditAccount': 26, 'description': '% BF (Delete)', 'mount': 1, },
    {'debitAccount': 158, 'creditAccount': 26, 'description': '% BG (Delete)', 'mount': 1, },
    {'debitAccount': 170, 'creditAccount': 26, 'description': '% BG+ (Delete)', 'mount': 1, },
    {'debitAccount': 65, 'creditAccount': 26, 'description': '% BMSC (Delete)', 'mount': 1, },
    {'debitAccount': 43, 'creditAccount': 26, 'description': '% BNB (Delete)', 'mount': 0, },
    {'debitAccount': 143, 'creditAccount': 26, 'description': '% BS (Delete)', 'mount': 1, },
    {'debitAccount': 57, 'creditAccount': 26, 'description': '% BU (Delete)', 'mount': 1, },
    {'debitAccount': 115, 'creditAccount': 26, 'description': '% BCP (Delete)', 'mount': 1, },

    ### Fondo de Ahorro Mensual (Intereses ganados)
    {'debitAccount': 160, 'creditAccount': 148, 'description': '% Staking Binance Exchange (Delete)', 'mount': 4, },

    ### Retiro de dinero para gastos de mes
    {'debitAccount': 167, 'creditAccount': 161, 'description': 'Retiro de p2p para presupuesto de mes (Delete)', 'mount': 1100, },
    {'debitAccount': 158, 'creditAccount': 18, 'description': 'Esos USDT de arriba (Delete)', 'mount': 16000, },

    ### Distribucion de presupuesto de mes
    {'debitAccount': 143, 'creditAccount': 158, 'description': 'Presupuesto Mensual (Delete)', 'mount': 15000, }, #BS

    # Distribucion en bancos
    {'debitAccount': 124, 'creditAccount': 143, 'description': 'Gastos - Streaming (Netflix) (Delete)', 'mount': 55, },      #BE
    {'debitAccount': 124, 'creditAccount': 143, 'description': 'Gastos - Supervivencia (Delete)', 'mount': 2000, },          #BE
    {'debitAccount': 156, 'creditAccount': 143, 'description': 'Gastos - Aporte Gustos (Delete)', 'mount': 2200, },          #BF
    {'debitAccount': 170, 'creditAccount': 143, 'description': 'Gastos - Expensas (Delete)', 'mount': 1000, },               #BG+
    {'debitAccount': 65, 'creditAccount': 143, 'description': 'Gastos - Aporte Pareja (Delete)', 'mount': 1000, },           #BMSC
    {'debitAccount': 43, 'creditAccount': 143, 'description': 'Gastos - Aporte Padres (Delete)', 'mount': 2000, },           #BNB
    {'debitAccount': 57, 'creditAccount': 143, 'description': 'Gastos - Yo (Delete)', 'mount': 1500, },                      #BU
    {'debitAccount': 115, 'creditAccount': 143, 'description': 'Gastos - Aporte Comidas Familia (Delete)', 'mount': 1000, }, #BCP

    # Distribucion externa, mi hermana
    {'debitAccount': 196, 'creditAccount': 143, 'description': 'Gastos - Aporte hermana menor (Delete)', 'mount': 600, }, #BNB de mi hermana

    # Distribucion en billeteras
    {'debitAccount': 200, 'creditAccount': 143, 'description': 'Gastos - Terapia (Delete)', 'mount': 400, },         #Billetera Altoke
    {'debitAccount': 119, 'creditAccount': 143, 'description': 'Gastos - Servicios fijos (Delete)', 'mount': 500, }, #Billetera Yape
    {'debitAccount': 208, 'creditAccount': 143, 'description': 'Gastos - Mascotas (Delete)', 'mount': 400, },        #Billetera Yolo
]

queryParamForDefault = 'initial'

mount = 0
for item in INITIAL_SEAT_DETAIL:
    if item['description'].startswith('Gastos -'):
        mount += item['mount']

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


