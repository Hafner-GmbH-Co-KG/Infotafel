import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tafelausgabe", "0002_content_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="eintrag",
            name="monitor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="legacy_entries",
                to="tafelausgabe.monitor",
            ),
        ),
    ]
