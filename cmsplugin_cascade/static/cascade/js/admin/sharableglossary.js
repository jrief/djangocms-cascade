
django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';

	var url = new URL(window.location.href);
	var $sel_shared_glossary = $('#id_shared_glossary');
	if ($sel_shared_glossary.length === 0)
		return;

	// create class handling the SharableGlossaryMixin
	django.cascade.SharableGlossaryMixin = ring.create({
		constructor: function() {
			this.$super();

			// move the select box for Shared Glossary just at the beginning of the form
			// $('.field-shared_glossary').detach().insertAfter($('label[for=id_glossary_0]'));

			if ($sel_shared_glossary.children('option').length > 1) {
				// set the value for 'Shared Settings' to that one provided by the URL
				if (url.searchParams.has('glossary')) {
					$sel_shared_glossary.val(url.searchParams.get('glossary'));
				}
				// add event handler to select box for 'Shared Settings'
				$sel_shared_glossary.change(this.toggleSharedGlossary);
			} else {
				// remove the select box to choose from 'Shared Settings', since it doesn't contain any options
				$('.field-shared_glossary').remove();
			}

			// handle checkbox 'Remember these settings as'
			$('#id_save_as_identifier').prop('disabled', true);
			$('#id_save_shared_glossary').change(this.toggleSharedSettingsIdentifier);
		},
		toggleSharedGlossary: function(event) {
			var glossary = event.target.value,
			    $save_shared_glossary = $('.form-row.field-save_shared_glossary'),
			    $save_as_identifier = $('.form-row.field-save_as_identifier');

			if (glossary) {
				$save_shared_glossary.hide();
				$save_as_identifier.hide();
				url.searchParams.set('glossary', glossary);
				window.location.href = url.href;
			} else {
				$save_shared_glossary.show();
				$save_as_identifier.show();
				url.searchParams.set('glossary', '');
				window.location.href = url.href;
			}
		},
		toggleSharedSettingsIdentifier: function(evt) {
			var $save_as_identifier = $('#id_save_as_identifier');

			if (evt.target.checked) {
				$save_as_identifier.prop('disabled', false);
			} else {
				$save_as_identifier.prop('disabled', true);
				$save_as_identifier.val('');
			}
		}
	});
});
