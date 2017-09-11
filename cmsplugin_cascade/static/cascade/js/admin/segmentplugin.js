
django.jQuery(function($) {
	'use strict';
	var $id_open_tag = $("#id_glossary_open_tag");
	var $glossary_condition = $("#id_glossary_condition").parents('.glossary-widget');

	// create class handling the client-side part of SegmentPlugin
	django.cascade.SegmentPlugin = ring.create(eval(django.cascade.ring_plugin_bases.SegmentPlugin), {
		constructor: function() {
			var self = this;
			this.$super();

			// register event handler on changing `open_tag` select box
			$id_open_tag.change(function(evt) {
				self.selectOpenTag(evt.target.value);
			});
			this.selectOpenTag($id_open_tag.val());

			// make the condition field as large as possible
			$("#id_glossary_condition").parents('.glossary-field').css({'width': '100%'});
			$("#id_glossary_condition").css({'width': '100%', 'padding-right': '0'});
		},
		selectOpenTag: function(val) {
			if (val == 'if' || val == 'elif') {
				$glossary_condition.show();
			} else {
				// `else` does not require a condition 
				$glossary_condition.hide();
			}
		}
	});
});
