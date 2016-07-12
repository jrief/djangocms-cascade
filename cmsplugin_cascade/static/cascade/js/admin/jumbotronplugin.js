django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of JumbotronPlugin
	var JumbotronPlugin, base_plugins = eval(django.cascade.base_plugins),
	    $thumbnail_img = $('.js-file-selector img.thumbnail_img'),
	    $fileIdInputSelector = $('.vForeignKeyRawIdAdminField'),
	    $backgroundInputSize = $('input[name="background-size"]'),
	    $backgroundWidthHeight = $('.glossary_background-width-height').closest('.glossary-widget');

	JumbotronPlugin = ring.create(base_plugins, {
		constructor: function() {
			var self = this;
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.field-glossary').before($('.field-image_file'));

			fileIdInputChanged();
			backgroundInputSizeChanged();
		}
	});

	$fileIdInputSelector.on('change', function() {
		window.setTimeout(fileIdInputChanged);
	});

	$backgroundInputSize.on('change', backgroundInputSizeChanged);

	function backgroundInputSizeChanged() {
		console.log('changed: ' + $(this).val());
		if ($(this).val() === 'width/height') {
			$backgroundWidthHeight.show();
		} else {
			$backgroundWidthHeight.hide();
		}
	}

	function fileIdInputChanged() {
		var $backgroundHorizontalPosition = $('#id_glossary_background-horizontal-position'),
		    $backgroundVerticalPosition = $('#id_glossary_background-vertical-position'),
		    $backgroundAttachment = $('#id_glossary_background-attachment'),
		    $backgroundRepeat = $('#id_glossary_background-repeat');
		console.log('fileIdInputChanged');
		if ($fileIdInputSelector.val()) {
			$backgroundHorizontalPosition.removeAttr('disabled');
			$backgroundHorizontalPosition.removeAttr('disabled');
			$backgroundAttachment.removeAttr('disabled');
			$backgroundRepeat.removeAttr('disabled');
			$backgroundInputSize.removeAttr('disabled');
		} else {
			$backgroundHorizontalPosition.attr('disabled', 'disabled');
			$backgroundVerticalPosition.attr('disabled', 'disabled');
			$backgroundAttachment.attr('disabled', 'disabled');
			$backgroundRepeat.attr('disabled', 'disabled');
			$backgroundInputSize.attr('disabled', 'disabled');
		}
	}

	new JumbotronPlugin();
});
