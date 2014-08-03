
django.jQuery(function($) {
	'use strict';

	django.cascade.SharableLinkPlugin = function() {
		var self = this,
			$sel_shared_glossary = $('#id_shared_glossary'),
			$save_as_identifier = $('#id_save_as_identifier');
		django.cascade.LinkPlugin.call(this);

		// add event handler to select box for 'Shared Settings'
		if ($sel_shared_glossary.children('option').length > 1) {
			$sel_shared_glossary.change(function(evt) {
				self.toggleSharedGlossary($(this).children('option:selected'));
			});
			// if shared glossary is set, hide fields marked as sharable
			this.toggleSharedGlossary($sel_shared_glossary.children('option:selected'));
		} else {
			// remove the select box to chose from shared glossaries, since it doesn't contain any options
			$('.field-shared_glossary').remove();
		}

		// handle checkbox 'Remember these settings as'
		$save_as_identifier.prop('disabled', 'disabled');
		$('#id_save_shared_glossary').change(toggleSharedSettingsIdentifier);

		function toggleSharedSettingsIdentifier(evt) {
			if (evt.target.checked) {
				$save_as_identifier.prop('disabled', '');
			} else {
				$save_as_identifier.prop('disabled', 'disabled');
				$save_as_identifier.val('');
			}
		}
	};
	django.cascade.SharableLinkPlugin.prototype = Object.create(django.cascade.LinkPlugin.prototype);
	django.cascade.SharableLinkPlugin.prototype.toggleSharedGlossary = function($option) {
		var glossary = $option.data('glossary'),
			$save_shared_glossary = $('.form-row.field-save_shared_glossary');
		if (glossary) {
			$save_shared_glossary.hide();
		} else {
			$save_shared_glossary.show();
		}
	};

});
