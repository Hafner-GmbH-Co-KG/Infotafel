from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from .models import Eintrag


def anzeige(request):
    now = timezone.now()
    entry = (
        Eintrag.objects.filter(Q(expire__isnull=True) | Q(expire__gt=now))
        .order_by("-created")
        .first()
    )
    return render(request, "tafelausgabe/anzeige.html", {"entry": entry, "now": now})


@login_required
def eingabe(request):
    status = ""
    dauer = request.POST.get("dauer", "")
    text = ""
    sopran = alt = tenor = bass = False

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        sopran = request.POST.get("sopran") == "on"
        alt = request.POST.get("alt") == "on"
        tenor = request.POST.get("tenor") == "on"
        bass = request.POST.get("bass") == "on"
        expire = None
        if dauer:
            try:
                expire = timezone.now() + timedelta(seconds=int(dauer))
            except ValueError:
                pass
        Eintrag.objects.create(
            user=request.user,
            text=text,
            sopran=sopran,
            alt=alt,
            tenor=tenor,
            bass=bass,
            expire=expire,
        )
        status = "Gespeichert"
        text = ""
        sopran = alt = tenor = bass = False

    history = Eintrag.objects.filter(user=request.user).order_by("-created")[:10]
    context = {
        "dauer": dauer,
        "text": text,
        "sopran": sopran,
        "alt": alt,
        "tenor": tenor,
        "bass": bass,
        "status": status,
        "history": history,
    }
    return render(request, "tafelausgabe/eingabe.html", context)
