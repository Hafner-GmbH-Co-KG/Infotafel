from django.conf import settings
from django.db import models


class Eintrag(models.Model):
    """Speichert einen Liedeintrag eines Benutzers."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eintraege"
    )
    text = models.TextField(blank=True)
    sopran = models.BooleanField(default=False)
    alt = models.BooleanField(default=False)
    tenor = models.BooleanField(default=False)
    bass = models.BooleanField(default=False)
    expire = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.created:%Y-%m-%d %H:%M} - {self.text[:20]}"

