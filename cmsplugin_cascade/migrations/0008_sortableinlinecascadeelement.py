from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0007_add_proxy_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='SortableInlineCascadeElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('glossary', models.JSONField(blank=True, default={})),
                ('order', models.PositiveIntegerField(db_index=True, verbose_name='Sort by')),
                ('cascade_element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sortinline_elements', to='cmsplugin_cascade.CascadeElement')),
            ],
            options={
                'ordering': ('order',),
                'db_table': 'cmsplugin_cascade_sortinline',
            },
        ),
    ]
