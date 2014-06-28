django.jQuery(function($) {
	'use strict';

	// if checkbox Image Shapes: Responsive is active, replace 'Image Size' against 'Container Height'
	(function() {
		var $image_responsive = $('#id_glossary_image-shapes_0'),
		$glossary_responsive = $('#id_glossary_responsive-height').parents('.glossary-widget'),
		$glossary_static = $('#id_glossary_image-size').parents('.glossary-widget');
		$image_responsive.change(function(evt) {
			toggleResponsive(evt.target.checked);
		});
		toggleResponsive($image_responsive.prop('checked'));

		function toggleResponsive(checked) {
			if (checked) {
				$glossary_responsive.show();
				$glossary_static.hide();
			} else {
				$glossary_responsive.hide();
				$glossary_static.show();
			}
		}
	})();

	// if shared glossary is set, hide 'Image Size' and 'Resize Optinon'
	(function() {
		var $shared_glossary = $('#id_shared_glossary'),
			$save_as_identifier = $('#id_save_as_identifier');
		if ($shared_glossary.children('option').length > 1) {
			// move the select box below 'Image Shapes'
			$('#id_glossary_image-shapes').parents('.glossary-widget').after($shared_glossary.parents('.form-row'));
			$shared_glossary.change(function(evt) {
				toggleSharedGlossary($(this).children('option:selected'));
			});
			toggleSharedGlossary($shared_glossary.children('option:selected'));
		} else {
			// remove the select box, since it doesn't contain any options
			$shared_glossary.parents('.form-row').remove();
		}

		function toggleSharedGlossary($option) {
			var glossary = $option.data('glossary');
			if (glossary) {
				$('#imageelement_form .glossary_image-size input').each(function(idx, elem) {
					var name = $(elem).attr('name').replace('image-size-', '');
					$(elem).val(glossary['image-size'][name])
					$(elem).prop('disabled', 'disabled');
				});
				$('#imageelement_form .glossary_resize-options input').each(function(idx, elem) {
					$(elem).prop('checked', glossary['resize-options'].indexOf($(elem).val()) >=0);
					$(elem).prop('disabled', 'disabled');
				});
				$('#imageelement_form .form-row.field-save_shared_glossary').hide();
			} else {
				$('#imageelement_form .glossary_image-size input').prop('disabled', '');
				$('#imageelement_form .glossary_resize-options input').prop('disabled', '');
				$('#imageelement_form .form-row.field-save_shared_glossary').show();
			}
		}

		// handle checkbox field 'Remember image size as'
		$save_as_identifier.prop('disabled', 'disabled');
		$('#id_save_shared_glossary').change(function(evt) {
			if (evt.target.checked) {
				$save_as_identifier.prop('disabled', '');
			} else {
				$save_as_identifier.prop('disabled', 'disabled');
				$save_as_identifier.val('');
			}
		});
	})();
});
