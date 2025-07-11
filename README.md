# Infotafel

Dieses Repository enthält zwei einfache Projektansätze für eine Informations-
tafel:

1. **Django-Projekt** unter `infotafel_project` – ein minimales Django-Setup
   zum Experimentieren mit Python.
2. **HTML/PHP-Skelett** unter `infotafel/htdocs` – ein leichtgewichtiges
   Grundgerüst, das sich später einfach erweitern lässt.

## Django-Projekt starten

Am einfachsten lässt sich das Projekt mit dem beiliegenden Skript
`start_infotafel.sh` starten. Es installiert die nötigen Pakete, lädt auf
Wunsch die aktuelle Version des Repositories herunter oder aktualisiert eine
bereits vorhandene Kopie, richtet eine virtuelle Umgebung ein und startet
anschließend den Entwicklungsserver.

```bash
./start_infotafel.sh
```

Die im Skript verwendete Repository-Adresse kann bei Bedarf in der Variablen
`REPO_URL` angepasst werden.

Alternativ können die Schritte manuell ausgeführt werden:

1. Abhängigkeiten installieren (z. B. in einer virtuellen Umgebung):
   ```bash
   pip install django
   ```
2. Datenbankmigrationen durchführen und Entwicklungsserver starten:
   ```bash
   cd infotafel_project
   python manage.py migrate
   python manage.py runserver
   ```
   Die Infotafel ist anschließend unter `http://127.0.0.1:8000/` erreichbar.

## Struktur des HTML/PHP-Skeletts

```
infotafel/
└── htdocs/
    ├── index.html         ← Anzeige der Infotafel
    ├── input.html         ← Eingabemaske
    ├── scripts/
    │   ├── archive.php    ← später zum Archivieren
    │   └── speicher.php   ← später zum Speichern von Eingaben
    └── data/
        ├── anzeige.json       ← aktueller Text und Stati
        ├── einstellungen.json ← Anzeigedauer
        └── archiv.json        ← Historie
```

Die Dateien enthalten vorerst nur Beispielinhalte und dienen als Grundlage
für spätere Erweiterungen.

## Liederanzeige-App

Im Django-Unterverzeichnis `tafelausgabe` befindet sich eine kleine App, die
die gewünschte Liederanzeige für Smartphones und Tablets nachbildet. Sie
umfasst eine Anzeige- und eine Eingabeseite:

* `http://127.0.0.1:8000/` – zeigt den aktuellen Liedtext in großen Lettern
  auf schwarzem Hintergrund. Die Felder **T**, **S**, **A** und **B** werden je
  nach Auswahl farbig hervorgehoben. Ist kein Text gespeichert, erscheint die
  Uhrzeit.
* `http://127.0.0.1:8000/eingabe/` – touch-freundliche Maske zum Eingeben des
  Liedtextes, der aktivierten Stimmen sowie einer optionalen Anzeigedauer.

Die Daten werden im `localStorage` des Browsers abgelegt und aktualisieren die
Anzeige sofort. Für eine kurze Demonstration reicht es somit aus, den
Django-Server zu starten und beide Seiten im gleichen Browser aufzurufen.
