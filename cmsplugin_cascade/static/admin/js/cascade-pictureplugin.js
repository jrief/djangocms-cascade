django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';
	// if checkbox Image Shapes: Responsive is active, replace 'Image Size' against 'Container Height'
	var $image_responsive = $('#id_glossary_image-shapes_0'),
		$glossary_responsive = $('#id_glossary_responsive-height').parents('.glossary-widget'),
		$glossary_static = $('#id_glossary_image-size').parents('.glossary-widget');

	// reorganize layout to be more intuitive to use
	// move Radio boxes for Link Target
	$('.glossary-widget.glossary_target').before($('.form-row.field-link_type'));
	// move the select box for Shared Glossary just before 'Image Shapes'
	$('.glossary-widget.glossary_image-shapes').before($('.form-row.field-shared_glossary'));

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

	django.cascade.toggleSharedGlossary = function($option) {
		var glossary = $option.data('glossary');
		if (glossary) {
			$('#id_glossary_image-shapes input').each(function(idx, elem) {
				$(elem).prop('checked', glossary['image-shapes'].indexOf($(elem).val()) >= 0);
				$(elem).prop('disabled', 'disabled');
			});
			toggleResponsive($image_responsive.prop('checked'));
			$('#id_glossary_responsive-height').val(glossary['responsive-height']).prop('disabled', 'disabled');
			$('#id_glossary_image-size[name$="width"]').val(glossary['image-size']['width']).prop('disabled', 'disabled');
			$('#id_glossary_image-size[name$="height"]').val(glossary['image-size']['height']).prop('disabled', 'disabled');
			$('#id_glossary_resize-options input').each(function(idx, elem) {
				$(elem).prop('checked', glossary['resize-options'].indexOf($(elem).val()) >= 0);
				$(elem).prop('disabled', 'disabled');
			});
			$('.field-save_shared_glossary.field-save_as_identifier').hide();
		} else {
			$('#id_glossary_image-shapes input').prop('disabled', '');
			$('#id_glossary_responsive-height').prop('disabled', '');
			$('#id_glossary_image-size[name$="width"]').prop('disabled', '');
			$('#id_glossary_image-size[name$="height"]').prop('disabled', '');
			$('#id_glossary_resize-options input').prop('disabled', '');
			$('.field-save_shared_glossary.field-save_as_identifier').show();
		}
	}
});
