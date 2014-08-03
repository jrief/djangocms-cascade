django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';

	django.cascade.LinkPlugin = {
		$link_type: $("#id_link_type"),
		$field_cmspage: $(".form-row.field-link_type .field-box.field-cms_page"),
		$field_exturl: $(".form-row.field-link_type .field-box.field-ext_url"),
		$field_mailto: $(".form-row.field-link_type .field-box.field-mail_to"),
		$link_target: $(".glossary-widget.glossary_target"),
		init: function() {
			var self = this;

			// register event handler on changing link type select box
			this.$link_type.change(function(evt) {
				self.toggleLinkTypes(evt.target.value);
			});
			this.toggleLinkTypes(this.$link_type.val());
		},
		toggleLinkTypes: function(linkType) {
			switch(linkType) {
			case 'cmspage':
				this.$field_cmspage.show();
				this.$field_exturl.hide();
				this.$field_mailto.hide();
				this.$link_target.show();
				break;
			case 'exturl':
				this.$field_cmspage.hide();
				this.$field_exturl.show();
				this.$field_mailto.hide();
				this.$link_target.show();
				break;
			case 'email':
				this.$field_cmspage.hide();
				this.$field_exturl.hide();
				this.$field_mailto.show();
				this.$link_target.show();
				break;
			default:
				this.$field_cmspage.hide();
				this.$field_exturl.hide();
				this.$field_mailto.hide();
				this.$link_target.hide();
				break;
			}
		}
	};

	$(document).ready(function() {
		Object.create(django.cascade.LinkPlugin).init();
	});
});
