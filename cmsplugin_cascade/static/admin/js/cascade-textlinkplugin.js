django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';

	django.cascade.toggleSharedGlossary = function($option) {
		var glossary = $option.data('glossary');
		if (glossary) {
			console.log(glossary);
			
			$('#id_link_type').val(glossary['link']['type']);
			$('#id_link_type').prop('disabled', 'disabled');
			//django.cascade.toggleLinkTypes(glossary['link']['type']);
			try {
				$('#id_cms_page').select2({'enabled': false});
			} catch(err) {
				console.log(typeof err);
			}
			$('#id_ext_url').prop('disabled', 'disabled');
			$('#id_mail_to').prop('disabled', 'disabled');
			$('#id_glossary_title').prop('disabled', 'disabled');
			$('#id_glossary_target input').each(function(idx, elem) {
				$(elem).prop('checked', glossary['target'] === $(elem).val());
				$(elem).prop('disabled', 'disabled');
			});
			$('.field-save_shared_glossary.field-save_as_identifier').hide();
		} else {
			$('#id_link_type').prop('disabled', '');
			try {
				$('#id_cms_page').select2({'enabled': true});
			} catch(err) {
				console.log(typeof err);
			}
			$('#id_ext_url').prop('disabled', '');
			$('#id_mail_to').prop('disabled', '');
			$('#id_glossary_title').prop('disabled', 'disabled');
			$('#id_glossary_target input').prop('disabled', '');
			$('.field-save_shared_glossary.field-save_as_identifier').show();
		}
	};
});
