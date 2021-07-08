from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0011_merge_sharable_with_cascadeelement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cascadeelement',
            name='shared_glossary',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmsplugin_cascade.SharedGlossary'),
        ),
    ]
