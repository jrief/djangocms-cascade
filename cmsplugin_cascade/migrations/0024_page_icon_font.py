from django.db import migrations, models
import django.db.models.deletion
from cmsplugin_cascade.models import CascadeElement, CascadePage, IconFont


def forwards(apps, schema_editor):
    for cascade_element in CascadeElement.objects.all():
        if cascade_element.plugin_type not in ['FramedIconPlugin', 'TextIconPlugin', 'BootstrapButtonPlugin']:
            continue
        try:
            cms_page = cascade_element.page.get_public_object()
            icon_font = cms_page.cascadepage.icon_font
            if not icon_font:
                continue
        except:
            continue
        if 'icon_font' not in cascade_element.glossary:
            cascade_element.glossary['icon_font'] = icon_font.pk
            cascade_element.save()


def backwards(apps, schema_editor):
    print("Backward migration not implemented")


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0023_iconfont_is_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cascadepage',
            name='icon_font',
            field=models.ForeignKey(blank=True, help_text='Deprecated', null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmsplugin_cascade.IconFont', verbose_name='Icon Font'),
        ),
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
