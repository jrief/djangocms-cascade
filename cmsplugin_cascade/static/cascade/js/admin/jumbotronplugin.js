django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of JumbotronPlugin
	var JumbotronPlugin, base_plugins = eval(django.cascade.base_plugins),
	    $fileIdInputSelector = $('.vForeignKeyRawIdAdminField'),
	    $backgroundColor = $('#id_glossary_background_color_color'),
	    $backgroundColorDisabled = $('#id_glossary_background_color_disabled'),
	    $backgroundInputSize = $('input[name="background_size"]'),
	    $backgroundWidthHeight = $('.glossary_background_width_height').closest('.glossary-widget');

	JumbotronPlugin = ring.create(base_plugins, {
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
				$backgroundHorizontalPosition.removeAttr('disabled');
				$backgroundVerticalPosition.removeAttr('disabled');
				$backgroundAttachment.removeAttr('disabled');
				$backgroundRepeat.removeAttr('disabled');
				$backgroundInputSize.removeAttr('disabled');
				$backgroundWidthHeight.find('input').removeAttr('disabled');
			} else {
				$backgroundHorizontalPosition.attr('disabled', 'disabled');
				$backgroundVerticalPosition.attr('disabled', 'disabled');
				$backgroundAttachment.attr('disabled', 'disabled');
				$backgroundRepeat.attr('disabled', 'disabled');
				$backgroundInputSize.attr('disabled', 'disabled');
				$backgroundWidthHeight.find('input').attr('disabled', 'disabled');
			}
		},
		backgroundDisabledChanged: function() {
			var $inputField = $('input[name="background_color_disabled"]:checked');
			if ($inputField.val() === 'on') {
				$backgroundColor.attr('disabled', 'disabled');
			} else {
				$backgroundColor.removeAttr('disabled');
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
			this.backgroundDisabledChanged();
			this.backgroundInputSizeChanged();
			this.$super && this.$super();
		}

	});

	new JumbotronPlugin();
});
