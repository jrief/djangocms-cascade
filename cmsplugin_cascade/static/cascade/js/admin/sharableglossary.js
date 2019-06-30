
django.cascade = django.cascade || {};

django.jQuery(function($) {
	'use strict';

	var url = new URL(window.location.href);
	var $sel_shared_glossary = $('#id_shared_glossary');
	if ($sel_shared_glossary.length === 0)
		return;

	// create class handling the SharableGlossaryMixin
	django.cascade.SharableGlossaryMixin = ring.create({
		constructor: function() {
			this.$super();

			if ($sel_shared_glossary.children('option').length > 1) {
				// set the value for 'Shared Settings' to that one provided by the URL
				if (url.searchParams.has('glossary')) {
					$sel_shared_glossary.val(url.searchParams.get('glossary'));
				}
				// add event handler to select box for 'Shared Settings'
				$sel_shared_glossary.change(this.toggleSharedGlossary);
			} else {
				// remove the select box to choose from 'Shared Settings', since it doesn't contain any options
				$('.field-shared_glossary').remove();
			}
		},
		toggleSharedGlossary: function(event) {
			var glossary = event.target.value;

			if (glossary) {
				url.searchParams.set('glossary', glossary);
				window.location.href = url.href;
			} else {
				url.searchParams.set('glossary', '');
				window.location.href = url.href;
			}
		}
	});
});
