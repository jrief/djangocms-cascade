django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of JumbotronPlugin
	var base_plugins = eval(django.cascade.ring_plugin_bases.JumbotronPlugin),
	    $fileIdInputSelector = $('#id_image_file'),
	    $backgroundInputSize = $('input[name="background_size"]'),
	    $backgroundWidthHeight = $('.form-row.field-background_width_height');

	django.cascade.JumbotronPlugin = ring.create(base_plugins, {
		constructor: function() {
			var self = this;
			this.$super();

			// install event handlers
			$fileIdInputSelector.on('change', function() {
				window.setTimeout(self.fileIdInputChanged);
			});
			$backgroundInputSize.on('change', self.backgroundInputSizeChanged);

			// set defaults
			this.refreshChangeForm();
		},
		fileIdInputChanged: function () {
			var $backgroundHorizontalPosition = $('#id_background_horizontal_position'),
			    $backgroundVerticalPosition = $('#id_background_vertical_position'),
			    $backgroundAttachment = $('input[name="background_attachment"]'),
			    $backgroundRepeat = $('input[name="background_repeat"]');
			if ($fileIdInputSelector.val()) {
				$backgroundHorizontalPosition.prop('disabled', false);
				$backgroundVerticalPosition.prop('disabled', false);
				$backgroundAttachment.prop('disabled', false);
				$backgroundRepeat.prop('disabled', false);
				$backgroundInputSize.prop('disabled', false);
				$backgroundWidthHeight.find('input').prop('disabled', false);
			} else {
				$backgroundHorizontalPosition.prop('disabled', true);
				$backgroundVerticalPosition.prop('disabled', true);
				$backgroundAttachment.prop('disabled', true);
				$backgroundRepeat.prop('disabled', true);
				$backgroundInputSize.prop('disabled', true);
				$backgroundWidthHeight.find('input').prop('disabled', true);
			}
		},
		backgroundInputSizeChanged: function() {
			var $inputField = $('input[name="background_size"]:checked');
			if ($inputField.val() === 'width/height') {
				$backgroundWidthHeight.show();
			} else {
				$backgroundWidthHeight.hide();
			}
		},
		refreshChangeForm: function() {
			this.fileIdInputChanged();
			this.backgroundInputSizeChanged();
			this.$super && this.$super();
		}

	});
});
