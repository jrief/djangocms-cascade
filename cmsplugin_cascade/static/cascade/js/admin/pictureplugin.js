
django.jQuery(function($) {
	'use strict';

	var PicturePlugin, base_plugins = eval(django.cascade.base_plugins);

	// create class handling the client-side part of PicturePlugin
	PicturePlugin = ring.create(base_plugins, {
		constructor: function() {
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));
		}
	});
	new PicturePlugin();
});
