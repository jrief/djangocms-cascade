
django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';

	var $sel_shared_glossary = $('#id_shared_glossary');
	if ($sel_shared_glossary.length === 0)
		return;

	// create class handling the SharableGlossaryMixin
	django.cascade.SharableGlossaryMixin = ring.create({
		constructor: function() {
			var self = this;
			this.$super();

			// move the select box for Shared Glossary just at the beginning of the form
			$('.field-shared_glossary').detach().insertAfter($('label[for=id_glossary_0]'));

			if ($sel_shared_glossary.children('option').length > 1) {
				// add event handler to select box for 'Shared Settings'
				$sel_shared_glossary.change(function(evt) {
					self.toggleSharedGlossary($(this).children('option:selected'));
				});
				// if shared glossary is set, hide fields marked as sharable
				this.toggleSharedGlossary($sel_shared_glossary.children('option:selected'));
			} else {
				// remove the select box to choose from shared glossaries, since it doesn't contain any options
				$('.field-shared_glossary').remove();
			}

			// handle checkbox 'Remember these settings as'
			$('#id_save_as_identifier').prop('disabled', 'disabled');
			$('#id_save_shared_glossary').change(this.toggleSharedSettingsIdentifier);
		},
		toggleSharedGlossary: function($option) {
			var glossary = $option.data('glossary'),
				$save_shared_glossary = $('.form-row.field-save_shared_glossary');

			if (glossary) {
				$save_shared_glossary.hide();
				// copy the values from the shared glossary back to the fields
				$.each(glossary, function(name, value) {
					if ($.isArray(value)) {
						$('input[name=' + name + ']').each(function(idx, elem) {
							$(elem).prop('checked', value.indexOf($(elem).val()) >= 0);
						});
					} else {
						$('input[name=' + name + ']').val(value);
					}
				});
				// disable some fields, since they obtain their values the shared glossary
				$.each(django.cascade.sharable_fields, function(k, element_id) {
					$('#' + element_id).prop('disabled', 'disabled');
				});
			} else {
				$save_shared_glossary.show();
				$.each(django.cascade.sharable_fields, function(k, element_id) {
					$('#' + element_id).prop('disabled', '');
				});
			}
			if (this.$super) {
				this.$super($option);
			} else {
				this.refreshChangeForm && this.refreshChangeForm();
			}
		},
		toggleSharedSettingsIdentifier: function(evt) {
			var $save_as_identifier = $('#id_save_as_identifier');

			if (evt.target.checked) {
				$save_as_identifier.prop('disabled', '');
			} else {
				$save_as_identifier.prop('disabled', 'disabled');
				$save_as_identifier.val('');
			}
		}
	});
});
