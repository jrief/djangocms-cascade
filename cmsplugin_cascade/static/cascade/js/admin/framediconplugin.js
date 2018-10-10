django.jQuery(function($) {
	'use strict';

	var $glossary_icon_align = $('#id_glossary_text_align').find('input[name="text_align"]'),
	    $glossary_font_size = $('#id_glossary_font_size').closest('.glossary-widget');

	// create class handling the client-side part of a FramedIconPlugin
	django.cascade.FramedIconPlugin = ring.create(eval(django.cascade.ring_plugin_bases.FramedIconPlugin), {
		constructor: function() {
			var self = this;
			this.$super();

			$glossary_icon_align.change(function(evt) {
				self.toggleAlignIcon(evt.target.value);
			});
		},
		toggleAlignIcon: function(iconAlign) {
			if (iconAlign === '') {
				$glossary_font_size.hide();
			} else {
				$glossary_font_size.show();
			}
		},
		refreshChangeForm: function() {
			var value;
			$.each($glossary_icon_align, function(index, field) {
				if (field.checked) {
					value = field.value;
					return;
				}
			});
			this.toggleAlignIcon(value);
			this.$super && this.$super();
		}
	});
});
