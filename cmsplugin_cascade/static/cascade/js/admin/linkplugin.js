
window['jQuery'] = jQuery || django.jQuery;  // re-add to global namespace since select2 otherwise does not work
django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';

	django.cascade.LinkPluginBase = ring.create({
		constructor: function() {
			var self = this, $link_type = $("#id_link_type");
			this.$super();

			// register event handler on changing link type select box
			$link_type.change(function(evt) {
				self.toggleLinkTypes(evt.target.value);
			});
			this.toggleLinkTypes($link_type.val());
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
				$link_target.show();
				break;
			default:
				$field_cmspage.hide();
				$field_exturl.hide();
				$field_mailto.hide();
				$link_target.hide();
				break;
			}
		}
	});
});
