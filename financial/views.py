# Create your views here.
from django.http import HttpResponse

def seat_report(request, id):
    return HttpResponse("Set Report " + str(id))
