
window['jQuery'] = jQuery || django.jQuery;  // re-add to global namespace since select2 otherwise does not work

django.jQuery(function($) {
	'use strict';
	var $link_type = $("#id_link_type");

	django.cascade.LinkPluginBase = ring.create({
		constructor: function() {
			var self = this;
			this.$super();

			// register event handler on changing link type select box
			$link_type.change(function(evt) {
				self.toggleLinkTypes(evt.target.value);
			});
			this.refreshChangeForm();
		},
		toggleLinkTypes: function(linkType) {
			var $field_cmspage = $(".form-row.field-link_type .field-box.field-cms_page"),
				$field_exturl = $(".form-row.field-link_type .field-box.field-ext_url"),
				$field_mailto = $(".form-row.field-link_type .field-box.field-mail_to"),
				$link_target = $(".glossary-widget .glossary_target");

			switch(linkType) {
			case 'cmspage':
				$field_cmspage.show();
				$field_exturl.hide();
				$field_mailto.hide();
				$link_target.show();
				break;
			case 'exturl':
				$field_cmspage.hide();
				$field_exturl.show();
				$field_mailto.hide();
				$link_target.show();
				break;
			case 'email':
				$field_cmspage.hide();
				$field_exturl.hide();
				$field_mailto.show();
				$link_target.hide();
				break;
			default:
				$field_cmspage.hide();
				$field_exturl.hide();
				$field_mailto.hide();
				$link_target.hide();
				break;
			}
		},
		toggleSharedGlossary: function($option) {
			var glossary = $option.data('glossary');
			try {
				$('#id_link_type').val(glossary['link']['type']);
				try {
					$("#id_cms_page").select2("data", {id: glossary['link']['pk'], text: glossary['link']['identifier']});
					$("#id_cms_page").select2('enable', false);
				} catch(err) {
					if (!(err instanceof TypeError))
						throw err;
					$("#id_cms_page").val(glossary['link']['pk']);
				}
				$('#id_ext_url').val(glossary['link']['url']);
				$('#id_mail_to').val(glossary['link']['email']);
			} catch (err) {
				try {
					if (!(err instanceof TypeError))
						throw err;
					$("#id_cms_page").select2('enable', true);
				} catch (err) {
					if (!(err instanceof TypeError))
						console.error(err);
				}
			}
			if (this.$super) {
				this.$super($option);
			} else {
				this.refreshChangeForm();
			}
		},
		refreshChangeForm: function() {
			this.toggleLinkTypes($link_type.val());
			this.$super && this.$super();
		}
	});
});
