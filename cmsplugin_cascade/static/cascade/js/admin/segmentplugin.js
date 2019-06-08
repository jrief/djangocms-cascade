
django.jQuery(function($) {
	'use strict';
	var $id_open_tag = $("#id_open_tag");
	var $condition_element = $(".field-condition");

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
		},
		selectOpenTag: function(val) {
			if (val == 'if' || val == 'elif') {
				$condition_element.show();
			} else {
				// `else` does not require a condition 
				$condition_element.hide();
			}
		}
	});
});
