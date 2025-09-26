from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import Eintrag
from .services import resolve_display_for_monitor, serialize_display_context


def anzeige(request, identifier=None):
    monitor_identifier = identifier or request.GET.get("monitor")
    display_context = resolve_display_for_monitor(monitor_identifier)
    display_payload = serialize_display_context(display_context)
    return render(
        request,
        "tafelausgabe/anzeige.html",
        {
            "display": display_payload,
            "monitor": display_payload.get("monitor", {}),
            "now": timezone.now(),
        },
    )


@require_GET
def monitor_state_api(request, identifier=None):
    monitor_identifier = identifier or request.GET.get("monitor")
    display_context = resolve_display_for_monitor(monitor_identifier)
    payload = serialize_display_context(display_context)
    return JsonResponse(payload)


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
