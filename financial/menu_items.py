from django.db import models
from django.urls import path
from django.contrib import admin

class Patrimony(models.Model):
    class Meta:
        verbose_name = "Patrimony"
        verbose_name_plural = "Patrimony"

class PatrimonyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class Flows(models.Model):
    class Meta:
        verbose_name = "Flow"
        verbose_name_plural = "Flows"

class FlowsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False