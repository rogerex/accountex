# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

def seat_report(request, id):
    context = {'seat_id': id}
    return render(request, 'reports/seat.html', context)
