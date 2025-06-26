# Infotafel

Dieses Repository enthält ein minimales Django-Projekt für eine Infotafel-Anwendung. Um die Anwendung lokal auszuführen benötigen Sie Python und Django.

## Setup

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
3. Die Infotafel ist anschließend unter `http://127.0.0.1:8000/` erreichbar.

Dieses Grundgerüss kann erweitert und an eigene Anforderungen angepasst werden.
