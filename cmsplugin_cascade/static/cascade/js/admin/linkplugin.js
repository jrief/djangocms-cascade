
django.jQuery(function($) {
	'use strict';
	var LinkPlugin, base_plugins = eval(django.cascade.base_plugins);

	// create class handling the client-side part of LinkPlugin
	LinkPlugin = ring.create(base_plugins, {});
	new LinkPlugin();
});
