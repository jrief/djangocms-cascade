django.jQuery(function($) {
	'use strict';
	var $checkboxElem = $('.form-row.field-save_settings_as input[type="checkbox"]');

	function saveAsChanged(checkboxInput) {
		var $identifierInput = $(checkboxInput).siblings('input[type="text"]');
		$identifierInput.prop('disabled', !checkboxInput.checked);
	}

	$checkboxElem.on('change', function(evt) {
		saveAsChanged(evt.target);
	});
	$.each($checkboxElem, function() {
		saveAsChanged(this);
	});

});
