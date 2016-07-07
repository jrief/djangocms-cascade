django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of JumbotronPlugin
	var JumbotronPlugin, base_plugins = eval(django.cascade.base_plugins),
	    $thumbnail_img = $('.js-file-selector img.thumbnail_img');

	JumbotronPlugin = ring.create(base_plugins, {
		constructor: function() {
			var self = this;
			this.$super();
		}
	});

	new JumbotronPlugin();
});
