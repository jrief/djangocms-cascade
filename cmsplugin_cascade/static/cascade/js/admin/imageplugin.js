
django.jQuery(function($) {
	'use strict';

	var $image_responsive = $('#id_glossary_image_shapes_0');

	// create class handling the client-side part of ImagePlugin
	django.cascade.ImagePlugin = ring.create(eval(django.cascade.ring_plugin_bases.ImagePlugin), {
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
				$image_width_fixed = $('#id_glossary_image_width_fixed').closest('.glossary-widget'),
				$image_alignment = $('#id_glossary_image_alignment').closest('.glossary-widget');

			// if checkbox Image Shapes: Responsive is active, show adaptive width and heights
			if (checked) {
				$image_width_responsive.show();
				$image_width_fixed.hide();
				$image_alignment.hide();
			} else {
				$image_width_responsive.hide();
				$image_width_fixed.show();
				$image_alignment.show();
			}
		},
		refreshChangeForm: function() {
			this.toggleResponsive($image_responsive.prop('checked'));
			this.$super && this.$super();
		}
	});
});
