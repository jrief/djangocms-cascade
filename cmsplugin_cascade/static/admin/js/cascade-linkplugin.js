django.jQuery(function($) {
	var $link_type = $("#id_link_type"),
		$field_pagelink = $("#linkelement_form .field-box.field-page_link"),
		$field_url = $("#linkelement_form .field-box.field-url"),
		$field_email = $("#linkelement_form .field-box.field-email");

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
