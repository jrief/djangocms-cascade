(function() {
	CKEDITOR.dtd.$removeEmpty.i = 0;
{% for icon_font in icon_fonts %}
	CMS.CKEditor.editor.addContentsCss('{{ icon_font.get_stylesheet_url }}');
{% endfor %}
})();
