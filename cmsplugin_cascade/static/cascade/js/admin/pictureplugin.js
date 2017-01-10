
django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of PicturePlugin
	django.cascade.PicturePlugin = ring.create(eval(django.cascade.ring_plugin_bases.PicturePlugin), {
		constructor: function() {
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));
		}
	});
});
