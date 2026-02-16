# CODEX_STRICT_MODE.md - Infotafel Codex Strict Mode (HARD)

Du arbeitest im Repository "Infotafel".

## 1) Arbeitsstil
- Mache nur kleine, isolierte Aenderungen.
- Jede Aenderung muss einen klaren Zweck haben und testbar sein.
- Keine Massen-Umbenennungen ohne Not.

## 2) Beweis statt Behauptung
- Vor Aenderungen: zeige per Inventur, wo du aenderst (Dateipfade, Funktionen, Call Sites).
- Nach Aenderungen: zeige Gate-Output oder klare Kommandos, wie der User sie ausfuehrt.

## 3) Reihenfolge ist verpflichtend
1) Ports/DTOs/Use-Case Skeleton (application/)
2) Adapter (adapters/)
3) Inbound (views/urls/forms)
4) Tests
5) Gates

## 4) Gates (muessen nach jeder Aufgabe gruen sein)
- Python Syntax: `python -m compileall -q .`
- Ruff: `python -m ruff check .`
- Ruff format: `python -m ruff format --check .`
- Pytest: `python -m pytest -q`
- Custom checks: siehe tools/checks/run_gates.(sh|ps1)

Wenn ein Gate fehlschlaegt: STOP, fixen, erneut laufen lassen.

## 5) Kontextpflege
Am Ende jeder Session:
- Kurzes "Update Infotafel:" (Bullets) mit:
  - Was wurde geaendert
  - Welche Dateien
  - Welche Gates liefen
  - Offene Risiken/ToDos
