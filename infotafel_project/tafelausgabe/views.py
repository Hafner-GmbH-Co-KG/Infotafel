from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .adapters.display.django_display_resolver import DjangoDisplayResolver
from .application.display.dtos import ResolveDisplayInput
from .application.display.use_cases import ResolveDisplay
from .forms import MonitorCreateForm, MonitorDeleteForm
from .models import Eintrag, Monitor

resolve_display_use_case = ResolveDisplay(resolver=DjangoDisplayResolver())


def anzeige(request, identifier=None):
    monitor_identifier = identifier or request.GET.get("monitor")
    display_payload = resolve_display_use_case.execute(
        ResolveDisplayInput(monitor_identifier=monitor_identifier)
    ).payload
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
    payload = resolve_display_use_case.execute(
        ResolveDisplayInput(monitor_identifier=monitor_identifier)
    ).payload
    return JsonResponse(payload)


@login_required
def eingabe(request):
    monitors = list(Monitor.objects.order_by("order", "name", "id"))
    if request.method == "POST":
        selected_monitor_id = request.POST.get("monitor", "")
    else:
        selected_monitor_id = request.GET.get("monitor") or ""
    selected_monitor = None
    if selected_monitor_id:
        for monitor in monitors:
            if (
                str(monitor.pk) == str(selected_monitor_id)
                or monitor.identifier == selected_monitor_id
            ):
                selected_monitor = monitor
                selected_monitor_id = str(monitor.pk)
                break

    status = ""
    dauer = request.POST.get("dauer", "")
    text = request.POST.get("text", "").strip() if request.method == "POST" else ""
    sopran = request.POST.get("sopran") == "on" if request.method == "POST" else False
    alt = request.POST.get("alt") == "on" if request.method == "POST" else False
    tenor = request.POST.get("tenor") == "on" if request.method == "POST" else False
    bass = request.POST.get("bass") == "on" if request.method == "POST" else False

    if request.method == "POST":
        expire = None
        if dauer:
            try:
                expire = timezone.now() + timedelta(seconds=int(dauer))
            except ValueError:
                expire = None
        Eintrag.objects.create(
            user=request.user,
            text=text,
            sopran=sopran,
            alt=alt,
            tenor=tenor,
            bass=bass,
            monitor=selected_monitor,
            expire=expire,
        )
        status = "Gespeichert"
        text = ""
        sopran = alt = tenor = bass = False

    history_qs = Eintrag.objects.filter(user=request.user)
    if selected_monitor is not None:
        history_qs = history_qs.filter(Q(monitor=selected_monitor) | Q(monitor__isnull=True))
    else:
        history_qs = history_qs.filter(monitor__isnull=True)
    history = history_qs.order_by("-created")[:10]

    context = {
        "dauer": dauer,
        "text": text,
        "sopran": sopran,
        "alt": alt,
        "tenor": tenor,
        "bass": bass,
        "status": status,
        "history": history,
        "monitors": monitors,
        "selected_monitor": selected_monitor,
        "selected_monitor_id": selected_monitor_id,
    }
    return render(request, "tafelausgabe/eingabe.html", context)


@login_required
def monitorverwaltung(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Nur fuer Team-Mitglieder verfuegbar.")

    create_form = MonitorCreateForm(prefix="create")
    delete_form = MonitorDeleteForm()

    if request.method == "POST":
        action = request.POST.get("mode")
        if action == "create":
            create_form = MonitorCreateForm(request.POST, prefix="create")
            if create_form.is_valid():
                monitor = create_form.save()
                link = request.build_absolute_uri(
                    reverse("monitor-anzeige", args=[monitor.identifier])
                )
                messages.success(
                    request,
                    f'Monitor "{monitor.name}" angelegt. Freigabelink: {link}',
                )
                return redirect("monitor-verwaltung")
        elif action == "delete":
            delete_form = MonitorDeleteForm(request.POST)
            if delete_form.is_valid():
                monitor = delete_form.delete()
                messages.success(request, f'Monitor "{monitor.name}" geloescht.')
                return redirect("monitor-verwaltung")
            else:
                for error_list in delete_form.errors.values():
                    for error in error_list:
                        messages.error(request, error)

    monitors = list(Monitor.objects.order_by("order", "name", "id"))
    for monitor in monitors:
        monitor.share_link = request.build_absolute_uri(
            reverse("monitor-anzeige", args=[monitor.identifier])
        )

    context = {
        "create_form": create_form,
        "delete_form": delete_form,
        "monitors": monitors,
    }
    return render(request, "tafelausgabe/monitore.html", context)
