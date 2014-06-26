django.jQuery(function($) {
	'use strict';

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
});
