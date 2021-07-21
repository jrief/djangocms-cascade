from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0024_page_icon_font'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextEditorConfigFields',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('element_type', models.CharField(choices=[('p', 'p'), ('h1', 'h1'), ('h2', 'h2'), ('h3', 'h3'), ('h4', 'h4'), ('h5', 'h5'), ('h6', 'h6'), ('pre', 'pre'), ('address', 'address'), ('div', 'div'), ('span', 'span')], max_length=12, verbose_name='Element Type')),
                ('css_classes', models.CharField(help_text='Freely selectable CSS classnames for this Text-Editor Style, separated by spaces.', max_length=250, verbose_name='CSS classes')),
            ],
            options={
                'verbose_name': 'Text Editor Config',
            },
        ),
    ]
