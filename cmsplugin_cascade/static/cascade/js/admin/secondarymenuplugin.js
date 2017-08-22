django.jQuery(function($) {
	// create class handling the client-side part of a BootstrapSecondaryMenuPlugin
	var $submenu_root = $("#id_glossary_page_id");

	django.cascade.SecondaryMenuPlugin = ring.create({
		constructor: function() {
			var self = this;
			this.$super();

			$submenu_root.change(function(evt) {
				self.toggleSubmenuRoot(evt.target.value);
			});
		},
		toggleSubmenuRoot: function(page_id) {
			console.log("page_id: " + page_id);
		}
	});
});
