
django.jQuery(function($) {
	'use strict';

	django.cascade.TextLinkPlugin = function() {
		django.cascade.SharableLinkPlugin.call(this);

		// move the select box for Shared Glossary just after 'LinkContent'
		$('.field-link_content').after($('.field-shared_glossary'));
	}
	django.cascade.TextLinkPlugin.prototype = Object.create(django.cascade.SharableLinkPlugin.prototype);
	django.cascade.TextLinkPlugin.prototype.toggleSharedGlossary = function($option) {
		var glossary = $option.data('glossary');
		if (glossary) {
			$('#id_link_type').val(glossary['link']['type']);
			$('#id_link_type').prop('disabled', 'disabled');
			this.toggleLinkTypes(glossary['link']['type']);
			try {
				$("#id_cms_page").select2("data", {id: glossary['link']['pk'], text: glossary['link']['identifier']});
				$("#id_cms_page").select2('enable', false);
			} catch(err) {
				$("#id_cms_page").val(glossary['link']['pk']);
				$('#id_cms_page').prop('disabled', 'disabled');
			}
			$('#id_ext_url').val(glossary['link']['url']);
			$('#id_ext_url').prop('disabled', 'disabled');
			$('#id_mail_to').val(glossary['link']['email']);
			$('#id_mail_to').prop('disabled', 'disabled');
			$('#id_glossary_title').val(glossary['title']);
			$('#id_glossary_title').prop('disabled', 'disabled');
			$('#id_glossary_target input').each(function(idx, elem) {
				$(elem).prop('checked', glossary['target'] === $(elem).val());
				$(elem).prop('disabled', 'disabled');
			});
			$('.field-save_shared_glossary.field-save_as_identifier').hide();
		} else {
			$('#id_link_type').prop('disabled', '');
			try {
				$("#id_cms_page").select2('enable', true);
			} catch(err) {
				$('#id_cms_page').prop('disabled', '');
			}
			$('#id_ext_url').prop('disabled', '');
			$('#id_mail_to').prop('disabled', '');
			$('#id_glossary_title').prop('disabled', '');
			$('#id_glossary_target input').prop('disabled', '');
			$('.field-save_shared_glossary.field-save_as_identifier').show();
		}
		django.cascade.SharableLinkPlugin.prototype.toggleSharedGlossary.call(this, $option);
	};

	new django.cascade.TextLinkPlugin();
});
