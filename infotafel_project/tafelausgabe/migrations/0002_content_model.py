from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tafelausgabe.models


def create_initial_display_state(apps, schema_editor):
    DisplayState = apps.get_model('tafelausgabe', 'DisplayState')
    DisplayState.objects.get_or_create(singleton_key='live')


class Migration(migrations.Migration):

    dependencies = [
        ('tafelausgabe', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('song', 'Lied'), ('bible', 'Bibel')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('language', models.CharField(blank=True, help_text='z. B. de, en', max_length=10)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_content_items', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_content_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('title',), 'verbose_name': 'Inhalt', 'verbose_name_plural': 'Inhalte'},
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.SlugField(max_length=60, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('front', 'Publikum'), ('stage', 'Buehne'), ('stream', 'Livestream'), ('control', 'Regie')], default='front', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('order', 'name'), 'verbose_name': 'Monitor', 'verbose_name_plural': 'Monitore'},
        ),
        migrations.CreateModel(
            name='Setlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('event_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_template', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_setlists', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-event_date', '-created_at'), 'verbose_name': 'Setliste', 'verbose_name_plural': 'Setlisten'},
        ),
        migrations.CreateModel(
            name='ContentSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0)),
                ('label', models.CharField(blank=True, max_length=50)),
                ('text', models.TextField(blank=True)),
                ('chords', models.TextField(blank=True, help_text='Akkorde fuer Musiker')),
                ('notes', models.TextField(blank=True, help_text='Interne Hinweise')),
                ('display_options', models.JSONField(blank=True, default=dict)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='tafelausgabe.contentitem')),
            ],
            options={'ordering': ('position', 'id'), 'verbose_name': 'Folie', 'verbose_name_plural': 'Folien', 'unique_together': {('item', 'position')}},
        ),
        migrations.CreateModel(
            name='BibleReference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.CharField(max_length=60)),
                ('chapter', models.PositiveIntegerField()),
                ('verse_start', models.PositiveIntegerField()),
                ('verse_end', models.PositiveIntegerField()),
                ('translation', models.CharField(default='LUT', max_length=30)),
                ('text', models.TextField(help_text='Text der Bibelstelle in der gewaehlten Uebersetzung')),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bible_reference', to='tafelausgabe.contentitem')),
            ],
            options={'verbose_name': 'Bibelstelle', 'verbose_name_plural': 'Bibelstellen'},
        ),
        migrations.CreateModel(
            name='SetlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField()),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('is_optional', models.BooleanField(default=False)),
                ('content_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setlist_items', to='tafelausgabe.contentitem')),
                ('setlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='tafelausgabe.setlist')),
            ],
            options={'ordering': ('position', 'id'), 'verbose_name': 'Setlisteneintrag', 'verbose_name_plural': 'Setlisteneintraege', 'unique_together': {('setlist', 'position')}},
        ),
        migrations.CreateModel(
            name='MonitorLayerConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layers', models.JSONField(default=tafelausgabe.models.default_layer_config)),
                ('monitor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='layer_config', to='tafelausgabe.monitor')),
            ],
            options={'verbose_name': 'Monitor-Layer', 'verbose_name_plural': 'Monitor-Layer'},
        ),
        migrations.CreateModel(
            name='MonitorContentOverride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layers', models.JSONField(blank=True, default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monitor_overrides', to='tafelausgabe.contentitem')),
                ('monitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_overrides', to='tafelausgabe.monitor')),
            ],
            options={'verbose_name': 'Monitor-Override', 'verbose_name_plural': 'Monitor-Overrides', 'unique_together': {('monitor', 'content_item')}},
        ),
        migrations.CreateModel(
            name='DisplayState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singleton_key', models.CharField(default='live', editable=False, max_length=20, unique=True)),
                ('visibility_overrides', models.JSONField(blank=True, default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='display_states', to='tafelausgabe.contentitem')),
                ('current_slide', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='display_states', to='tafelausgabe.contentslide')),
            ],
            options={'verbose_name': 'Anzeigestatus', 'verbose_name_plural': 'Anzeigestatus'},
        ),
        migrations.AlterModelOptions(
            name='eintrag',
            options={'verbose_name': 'Legacy-Eintrag', 'verbose_name_plural': 'Legacy-Eintraege'},
        ),
        migrations.AlterUniqueTogether(
            name='setlistitem',
            unique_together={('setlist', 'position')},
        ),
        migrations.AlterUniqueTogether(
            name='contentslide',
            unique_together={('item', 'position')},
        ),
        migrations.AlterUniqueTogether(
            name='monitorcontentoverride',
            unique_together={('monitor', 'content_item')},
        ),
        migrations.RunPython(create_initial_display_state, migrations.RunPython.noop),
    ]

