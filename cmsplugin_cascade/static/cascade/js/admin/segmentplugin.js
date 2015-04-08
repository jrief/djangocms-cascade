
django.jQuery(function($) {
	'use strict';
	var $id_open_tag = $("#id_glossary_open_tag");
	var $id_glossary_condition = $("#id_glossary_condition").parents('.glossary-widget');
	var SegmentPlugin, base_plugins = eval(django.cascade.base_plugins);

	// create class handling the client-side part of SegmentPlugin
	SegmentPlugin = ring.create(base_plugins, {
		constructor: function() {
			var self = this;
			this.$super();

			// register event handler on changing `open_tag` select box
			$id_open_tag.change(function(evt) {
				self.selectOpenTag(evt.target.value);
			});
			this.selectOpenTag($id_open_tag.val());
		},
		selectOpenTag: function(val) {
			if (val == 'if' || val == 'elif') {
				$id_glossary_condition.show();
			} else {
				// `else` does not require a condition 
				$id_glossary_condition.hide();
			}
		}
	});
	new SegmentPlugin();
});
