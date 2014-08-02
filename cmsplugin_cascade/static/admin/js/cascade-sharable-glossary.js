django.jQuery(function($) {
	'use strict';

	// if shared glossary is set, hide 'Image Size' and 'Resize Optinon'
	(function() {
		var $sel_shared_glossary = $('#id_shared_glossary'),
			$save_as_identifier = $('#id_save_as_identifier');
		if ($sel_shared_glossary.children('option').length > 1) {
			$sel_shared_glossary.change(function(evt) {
				django.cascade.toggleSharedGlossary($(this).children('option:selected'));
			});
			django.cascade.toggleSharedGlossary($sel_shared_glossary.children('option:selected'));
		} else {
			// remove the select box to chose from shared glossaries, since it doesn't contain any options
			$('.field-shared_glossary').remove();
		}

		// handle checkbox field 'Shared Settings'
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
