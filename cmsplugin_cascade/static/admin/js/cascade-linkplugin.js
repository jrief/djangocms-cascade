django.jQuery(function($) {
	'use strict';

	var $link_type = $("#id_link_type"),
		$field_pagelink = $(".form-row.field-link_type .field-box.field-page_link"),
		$field_url = $(".form-row.field-link_type .field-box.field-url"),
		$field_email = $(".form-row.field-link_type .field-box.field-email"),
		$link_target = $(".glossary-widget.glossary_target");

	$link_type.change(function(evt) {
		toggleLinkTypes(evt.target.value);
	});
	toggleLinkTypes($link_type.val());

	function toggleLinkTypes(linkType) {
		switch(linkType) {
		case 'int':
			$field_pagelink.show();
			$field_url.hide();
			$field_email.hide();
			$link_target.show();
			break;
		case 'ext':
			$field_pagelink.hide();
			$field_url.show();
			$field_email.hide();
			$link_target.show();
			break;
		case 'email':
			$field_pagelink.hide();
			$field_url.hide();
			$field_email.show();
			$link_target.show();
			break;
		default:
			$field_pagelink.hide();
			$field_url.hide();
			$field_email.hide();
			$link_target.hide();
			break;
		}
	}
});
