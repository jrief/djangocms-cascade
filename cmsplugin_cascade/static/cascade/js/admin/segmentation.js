
django.jQuery(function($) {
	'use strict';

	function reloadBrowser() {
		var parent = (window.parent) ? window.parent : window;
		parent.setTimeout(function () {
			parent.location.reload()
		}, 0);
	}

	$('#result_list a.emulate-user').each(function(idx, element) {
		var data = {'href': $(element).attr('href')};
		$(element).on('click', data, function(event) {
			$.get(data.href).then(reloadBrowser);
			return false;
		});
	});
});
