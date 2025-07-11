from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def anzeige(request):
    return render(request, 'tafelausgabe/anzeige.html')


@login_required
def eingabe(request):
    return render(request, 'tafelausgabe/eingabe.html')
