from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
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
    """Handle form input and show user's history."""
    status = "Gespeichert" if request.GET.get("saved") == "1" else ""
    dauer = ""
    text = ""
    sopran = alt = tenor = bass = False

    if request.method == "POST":
        dauer = request.POST.get("dauer", "")
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
        return redirect(f"{reverse('eingabe')}?saved=1")

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
