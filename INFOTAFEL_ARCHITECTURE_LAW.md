# INFOTAFEL_ARCHITECTURE_LAW.md (HARD)

## 1) Layering
Domain <- Application <- (Inbound, Adapters)

### Domain
Erlaubt:
- Dataclasses, Enums, Value Objects, Policies
- Reine Logik

Verboten:
- django.*, ORM, Models
- HTTP Request/Response
- timezone.now() direkt (Clock-Port statt dessen)
- Filesystem/JSON read/write

### Application
Erlaubt:
- Use-Cases (Verb+Object), DTOs, Result/Errors
- Ports (Repository Interfaces, Clock, Transaction)

Verboten:
- django imports
- ORM queries
- Template rendering

### Adapters (Outbound)
Erlaubt:
- Django ORM Repositories
- Legacy JSON Reader/Writer (uebergangsweise)
- Mapping in DTOs

Verboten:
- Fachliche Orchestrierung (das gehoert in Use-Cases)

### Inbound (Django)
Erlaubt:
- Views/Forms: parse/validate/map, call Use-Case, map response
Verboten:
- Businessentscheidungen
- Komplexe Queries (geh in Repos)

## 2) Use-Case Regeln
- Name: VerbObject, z.B. ResolveDisplay, CreateLegacyEntry, ListMonitors
- Input DTO + Output DTO + Result/Error
- Keine "God DTOs": pro Use-Case nur was gebraucht wird.

## 3) Legacy-Strategie
- Legacy Datenquellen (z.B. Eintrag/JSON) sind Adapters.
- Application entscheidet ueber Fallback/Reihenfolge, nicht Views.
- Migrationen sind nachvollziehbar (ADR oder docs/migration/*).

## 4) Typisierung
- DTOs als dataclasses (oder TypedDict, falls noetig).
- Keine riesigen Dict[str, Any] Payloads in Application (nur am Rand in Inbound).
