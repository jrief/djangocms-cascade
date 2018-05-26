
django.jQuery(function($) {
	'use strict';

	django.cascade.SphinxDocsLinkPlugin = ring.create(eval(django.cascade.ring_plugin_bases.SphinxDocsLinkPlugin), {
		constructor: function() {
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));
		},
		initializeLinkTypes: function() {
			this.$super();
			this.linkTypes['documentation'] = new this.LinkType('.form-row .field-box.field-documentation', true);
		}
	});
});
