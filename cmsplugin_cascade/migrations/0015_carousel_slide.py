import re
import warnings
from html.parser import HTMLParser
from django.db import migrations
from cms.api import add_plugin
from cms.models.pluginmodel import CMSPlugin
from djangocms_text_ckeditor.cms_plugins import TextPlugin
from cmsplugin_cascade.models import CascadeElement


def _replace_text_body(old_body, input_pattern, output_tag, id_format):
    regex = re.compile(input_pattern)

    def _do_replace(match):
        before_id, old_plugin_id, after_id = match.groups()

        if not old_plugin_id:
            return ''

        bits = []

        if before_id:
            bits.append(before_id.strip())

        bits.append(id_format.format(old_plugin_id))

        if after_id:
            bits.append(after_id.strip())

        # By using .join() we ensure the correct
        # amount of spaces are used to separate the different
        # attributes.
        tag_attrs = ' '.join(bits)
        return output_tag.format(tag_attrs)

    new_body, count = regex.subn(_do_replace, old_body)
    return new_body, count


def forwards(apps, schema_editor):
    html_parser = HTMLParser()

    for cascade_element in CascadeElement.objects.all():
        if cascade_element.plugin_type != 'CarouselSlidePlugin':
            continue

        caption = cascade_element.glossary.get('caption')
        if not caption:
            continue

        text_element = add_plugin(cascade_element.placeholder, TextPlugin, cascade_element.language,
                                  target=cascade_element)

        old_body = html_parser.unescape(caption)
        new_body, count = _replace_text_body(
            old_body,
            input_pattern=r'<img ([^>]*)\bid="plugin_obj_(?P<pk>\d+)"([^>]*)/?>',
            output_tag='<cms-plugin {}></cms-plugin>',
            id_format='id="{}"',
        )
        text_element.body = new_body
        text_element.save()

        # TODO: need to be re-tested
        if False and count > 0:
            for link_element in CMSPlugin.objects.filter(parent_id__in=(cascade_element.id, cascade_element.parent_id), plugin_type='TextLinkPlugin'):
                # print("Move Link {} from {} -> {}".format(link_element.id, link_element.parent_id, text_element.id))
                link_element.move(text_element, pos='last-child')
                link_element.save()


def backwards(apps, schema_editor):
    warnings.warn("Backward migration for Carousel Slide Plugins is not supported. Please check them manually.")


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0014_glossary_field'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
