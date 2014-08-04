django.jQuery(function($) {
	'use strict';

	var breakpoints = ['lg', 'md', 'sm', 'xs'], k;

	(function() {
		var $elem, checked_widest, checked_narrowest, data;
		for (k = 0; k < 4; k++) {
			data = {'selgroup': 'narrowest'};
			$elem = $('#id_glossary_widest_' + k);
			$elem.change(data, adoptSelection);
			if ($elem.prop('checked')) {
				checked_widest = k;
			}
		}
		for (k = 0; k < 4; k++) {
			data = {'selgroup': 'widest'};
			$elem = $('#id_glossary_narrowest_' + k);
			$elem.change(data, adoptSelection);
			if ($elem.prop('checked')) {
				checked_narrowest = k;
			}
		}
		for (k = 0; k < 4; k++) {
			setProperties($('#id_glossary_widest_' + k), k > checked_narrowest);
			setProperties($('#id_glossary_narrowest_' + k), k < checked_widest);
		}
	})();

	function adoptSelection(evt) {
		var i, index = breakpoints.indexOf(evt.target.value);
		console.log(evt);
		if (evt.data.selgroup === 'widest') {
			for (i = 0; i < 4; i++) {
				setProperties($('#id_glossary_widest_' + i), i > index);
			}
		} else if (evt.data.selgroup === 'narrowest') {
			for (i = 0; i < 4; i++) {
				setProperties($('#id_glossary_narrowest_' + i), i < index);
			}
		}
	}

	function setProperties($elem, disabled) {
		$elem.prop('disabled', disabled);
		if (disabled) {
			$elem.prop('checked', false);
			$elem.parents('.field-box').addClass('disabled');
		} else {
			$elem.parents('.field-box').removeClass('disabled');
		}
	}
});
