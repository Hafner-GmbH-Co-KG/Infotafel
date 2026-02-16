# ADR 0001: Anzeige-Aufloesung ueber Application-Use-Case kapseln

- Status: Akzeptiert
- Datum: 2026-02-16

## Kontext

Die Django-Views `anzeige` und `monitor_state_api` haben direkt auf die Service-Funktionen
`resolve_display_for_monitor` und `serialize_display_context` zugegriffen.
Dadurch war keine explizite Application-Grenze zwischen Inbound und Adapter sichtbar.

## Entscheidung

Wir fuehren einen kleinen Application-Slice ein:

- `ResolveDisplayInput` und `ResolveDisplayOutput` als DTOs
- `DisplayResolverPort` als Port-Interface
- `ResolveDisplay` als Use-Case
- `DjangoDisplayResolver` als Adapter, der die bestehenden Service-Funktionen nutzt

Die Views rufen nur noch den Use-Case auf.

## Konsequenzen

- Inbound ist klarer von der Django-basierten Aufloesungslogik entkoppelt.
- Bestehendes Verhalten bleibt erhalten, weil der Adapter weiterhin den bisherigen
  Service benutzt.
- Die Application-Logik ist isoliert testbar (Use-Case-Test ohne Django-Setup).
