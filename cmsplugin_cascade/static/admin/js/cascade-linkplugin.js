django.jQuery(function($) {
	'use strict';

	var $link_type = $("#id_link_type"),
		$field_pagelink = $("#id_page_link_0").parent(".field-box"),
		$field_url = $("#id_url").parent(".field-box"),
		$field_email = $("#id_email").parent(".field-box");

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
			break;
		case 'ext':
			$field_pagelink.hide();
			$field_url.show();
			$field_email.hide();
			break;
		case 'email':
			$field_pagelink.hide();
			$field_url.hide();
			$field_email.show();
			break;
		default:
			$field_pagelink.hide();
			$field_url.hide();
			$field_email.hide();
			break;
		}
	}
});
