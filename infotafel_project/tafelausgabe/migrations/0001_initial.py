from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Eintrag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True)),
                ('sopran', models.BooleanField(default=False)),
                ('alt', models.BooleanField(default=False)),
                ('tenor', models.BooleanField(default=False)),
                ('bass', models.BooleanField(default=False)),
                ('expire', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eintraege', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
