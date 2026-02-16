# CODEX.md - Infotafel Engineering Law (HARD)

Dieses Repository wird durch die folgenden Gesetze fuer Struktur, Sprache, Architektur, Tests und Arbeitsweise geregelt.
Jede Abweichung ist ein Fehler und muss korrigiert werden.

## 1) Ziel
- Wartbar, testbar, sicher deploybar.
- Keine "Big Bang"-Umschreibung.
- Kleine, reviewbare Aenderungen.

## 2) Sprache
### 2.1 Code
- Alle Code-Identifier sind Englisch:
  - Python module/package names, classes, functions, variables
  - Django app names, model field names, settings keys
  - URLs / route names / API keys
- Kommentare im Code: Englisch oder Deutsch erlaubt, aber kurz.

### 2.2 Dokumentation
- Dokumentation in docs/* ist Deutsch.
- Commit-Messages: Deutsch oder Englisch, aber praezise.

## 3) Struktur (Repository)
Pflichtpfade:
- docs/adr/                Architekturentscheidungen
- tools/checks/            Gates / Checks
- infotafel_project/       Django Projekt (bestehend)
- infotafel_project/tafelausgabe/  Django App (bestehend)

Neue Strukturkonvention fuer Clean Architecture innerhalb der App:
- infotafel_project/tafelausgabe/application/
- infotafel_project/tafelausgabe/domain/
- infotafel_project/tafelausgabe/adapters/
- infotafel_project/tafelausgabe/inbound/

Hinweis: Django bleibt Framework/Delivery. Domain/Application bleiben framework-frei.

## 4) Architekturgesetz (Clean Architecture light fuer Django)
- Domain: rein fachlich, keine Django/ORM/HTTP/Timezone imports.
- Application: Use-Cases orchestrieren, sprechen nur ueber Ports/Interfaces.
- Adapters: Implementieren Ports (Django ORM, Dateisystem, Legacy JSON, etc.).
- Inbound: Django Views/Forms/URLs (nur Request/Response Mapping, keine Fachentscheidungen).

## 5) Arbeitsreihenfolge (immer)
1) Inventur (nur lesen): relevante Dateien/Dependencies/Existing Patterns finden.
2) Plan: minimaler Slice, betroffene Dateien, Risiken, Tests.
3) Domain/Application definieren (Entities/DTOs/Ports/Use-Case).
4) Adapter implementieren.
5) Inbound anbinden (Views/URLs/Forms).
6) Gates ausfuehren und gruen machen.

## 6) Anti-Codeklumpen (Limits)
- Max 300 Zeilen pro Datei (Ausnahme: Django migrations, auto-generated).
- Max 60 Zeilen pro Funktion.
- Max 12 public methods pro Klasse.
Wenn ueberschritten: splitten (Mapper/Policy/Service/DTO).

## 7) Daten / Source of Truth
- SQLite ist fuer Dev ok; produktiv konfigurierbar ueber ENV.
- Legacy JSON (falls genutzt) ist nur uebergangsweise; Migrationen muessen dokumentiert sein.

## 8) Doku-Pflicht
Wenn Verhalten, DB, API oder Deploy sich aendert:
- CHANGELOG.md aktualisieren ODER
- ADR in docs/adr/ schreiben.

## 9) Nicht raten
Wenn etwas unklar ist:
- erst Inventur (ripgrep/grep, Django settings, urls, models),
- dann Plan,
- dann Aenderung.

## ⛏️ Option A – Immediate Baseline Cleanup (HARD RULE)

Wenn „ruff check .“ oder „ruff format --check .“ im Repository Fehler meldet, muss eine **Baseline-Bereinigung** erfolgen, bevor ein Feature-Slice in main gemerged wird.

### Regeln

1) **Alle Ruff-Fehler müssen beseitigt werden**.
   - Keine Ignorierung über `noqa`.
   - Keine dauerhafte Deaktivierung im config.
   - Auch Legacy-Code muss korrigiert werden.

2) **Fix-Befehle sind verpflichtend:**
   ```bash
   python -m ruff check . --fix
   python -m ruff format .
