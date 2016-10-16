
django.jQuery(function($) {
	'use strict';

	var ImagePlugin,
	    $image_responsive = $('#id_glossary_image_shapes_0'),
	    base_plugins = eval(django.cascade.base_plugins);

	// create class handling the client-side part of ImagePlugin
	ImagePlugin = ring.create(base_plugins, {
		constructor: function() {
			var self = this;
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));

			// install event handlers
			$image_responsive.change(function(evt) {
				self.toggleResponsive(evt.target.checked);
			});
			this.refreshChangeForm();
		},
		toggleResponsive: function(checked) {
			var $image_width_responsive = $('#id_glossary_image_width_responsive').closest('.glossary-widget'),
				$image_width_fixed = $('#id_glossary_image_width_fixed').closest('.glossary-widget');

			// if checkbox Image Shapes: Responsive is active, show adaptive width and heights
			if (checked) {
				$image_width_responsive.show();
				$image_width_fixed.hide();
			} else {
				$image_width_responsive.hide();
				$image_width_fixed.show();
			}
		},
		refreshChangeForm: function() {
			this.toggleResponsive($image_responsive.prop('checked'));
			this.$super && this.$super();
		}
	});

	new ImagePlugin();
});
