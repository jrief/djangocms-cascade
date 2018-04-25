django.jQuery(function($) {
	// create class handling the client-side part of a TextImagePlugin
	django.cascade.TextImagePlugin = ring.create(eval(django.cascade.ring_plugin_bases.TextImagePlugin), {
		constructor: function() {
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));
		}
	});
});
