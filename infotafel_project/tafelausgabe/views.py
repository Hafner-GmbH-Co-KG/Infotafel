from django.shortcuts import render


def anzeige(request):
    return render(request, 'tafelausgabe/anzeige.html')


def eingabe(request):
    return render(request, 'tafelausgabe/eingabe.html')
