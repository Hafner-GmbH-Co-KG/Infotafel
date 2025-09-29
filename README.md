# Infotafel

Django-Projekt zur Steuerung einer digitalen Lied- und Hinweis-Anzeige. Der Fokus liegt wieder voll auf der Django-App im Ordner infotafel_project.

## Schnellstart

1. Virtuelle Umgebung anlegen: python -m venv .venv
2. Aktivieren und Abhaengigkeiten installieren: pip install -r requirements.txt
3. In das Django-Verzeichnis wechseln: cd infotafel_project
4. Datenbank vorbereiten: python manage.py migrate
5. Optional Admin-Benutzer: python manage.py createsuperuser
6. Server starten: python manage.py runserver

Die Django-Instanz laeuft standardmaessig unter http://localhost:8000/.

## Wichtige URLs

- / - Anzeige fuer Besucher. Optional ?monitor=<slug> zum Umschalten.
- /monitor/<slug>/ - Direkter Freigabelink fuer einen Monitor.
- /monitore/ - Neue Verwaltungsoberflaeche fuer virtuelle Monitore (Login und is_staff notwendig).
- /eingabe/ - Einfache Eingabeseite fuer kurzfristige Anzeigen (Login erforderlich).

## Monitore verwalten

Die Seite /monitore/ erlaubt das Anlegen, Loeschen und Teilen von virtuellen Monitoren direkt in Django. Beim Anlegen wird automatisch ein eindeutiger Kurzname erzeugt und ein Standard-Layer-Profil hinterlegt. Die angezeigten Freigabelinks verweisen auf die Django-Ansichten und koennen direkt im Browser oder auf Endgeraeten verwendet werden.

## Legacy-Daten importieren

Alte JSON-Daten aus dem frueheren PHP-Setup liegen weiterhin unter Infotafel/htdocs/data. Mit dem Befehl

    cd infotafel_project
    python manage.py import_legacy_data

lassen sich Monitore und Inhalte in die aktuelle Datenbank uebernehmen. Falls die Daten an einem anderen Ort liegen, kann der Pfad mit --base-dir <pfad> angegeben werden. Die Optionen --skip-monitors, --skip-content sowie --user <username> erlauben eine feinere Steuerung.

## Hinweis zum PHP-Ordner

Die Dateien im Verzeichnis Infotafel/htdocs dienen nur noch als Datenquelle fuer den Import. Die eigentliche Weboberflaeche und API werden komplett durch Django bereitgestellt.
