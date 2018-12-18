django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of ButtonPlugin
	var $glossary_icon_align = $('#id_glossary_icon_align').find('input[name="icon_align"]'),
	    $glossary_icon_font = $('.glossary_icon_font').parent('.glossary-widget'),
	    $glossary_symbol = $('.glossary_symbol').parent('.glossary-widget');

	django.cascade.ButtonMixin = ring.create(eval(django.cascade.ring_plugin_bases.ButtonMixin), {
		constructor: function() {
			var self = this;
			this.$super();
			if (django.cascade.hasOwnProperty('IconPluginMixin')) {
				$glossary_icon_align.change(function(evt) {
					self.toggleAlignIcon(evt.target.value);
				});
			} else {
				$glossary_icon_align.prop('disabled', true);
			}
			this.refreshChangeForm();
		},
		toggleAlignIcon: function(iconAlign) {
			if (iconAlign === '') {
				$glossary_icon_font.hide();
				$glossary_symbol.hide();
			} else {
				$glossary_icon_font.show();
				$glossary_symbol.show();
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
