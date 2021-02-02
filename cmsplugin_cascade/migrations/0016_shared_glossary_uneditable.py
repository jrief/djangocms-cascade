from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0015_carousel_slide'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cascadeelement',
            name='shared_glossary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmsplugin_cascade.SharedGlossary'),
        ),
        migrations.AlterModelOptions(
            name='cascadeelement',
            options={'verbose_name': 'Element'},
        ),
    ]
