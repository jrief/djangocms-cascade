django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of JumbotronPlugin
	var base_plugins = eval(django.cascade.ring_plugin_bases.JumbotronPlugin),
	    $fileIdInputSelector = $('.vForeignKeyRawIdAdminField'),
	    $backgroundColor = $('#id_glossary_background_color_color'),
	    $backgroundColorDisabled = $('#id_glossary_background_color_disabled'),
	    $backgroundInputSize = $('input[name="background_size"]'),
	    $backgroundWidthHeight = $('.glossary_background_width_height').closest('.glossary-widget');

	django.cascade.JumbotronPlugin = ring.create(base_plugins, {
		constructor: function() {
			var self = this;
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.field-glossary').before($('.field-image_file'));

			// install event handlers
			$fileIdInputSelector.on('change', function() {
				window.setTimeout(self.fileIdInputChanged);
			});
			$backgroundColorDisabled.on('change', self.backgroundDisabledChanged);
			$backgroundInputSize.on('change', self.backgroundInputSizeChanged);

			// set defaults
			this.refreshChangeForm();
		},
		fileIdInputChanged: function () {
			var $backgroundHorizontalPosition = $('#id_glossary_background_horizontal_position'),
			    $backgroundVerticalPosition = $('#id_glossary_background_vertical_position'),
			    $backgroundAttachment = $('#id_glossary_background_attachment'),
			    $backgroundRepeat = $('#id_glossary_background_repeat');
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
		backgroundDisabledChanged: function() {
			var $inputField = $('input[name="background_color_disabled"]:checked');
			$backgroundColor.prop('disabled', $inputField.val() === 'on');
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
			this.backgroundDisabledChanged();
			this.backgroundInputSizeChanged();
			this.$super && this.$super();
		}

	});
});
