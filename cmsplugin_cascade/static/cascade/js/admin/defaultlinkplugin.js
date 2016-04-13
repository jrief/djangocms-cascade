
django.jQuery(function($) {
	'use strict';
	var DefaultLinkPlugin, base_plugins = eval(django.cascade.base_plugins);

	// create class handling the client-side part of LinkPlugin
	DefaultLinkPlugin = ring.create(base_plugins, {});
	new DefaultLinkPlugin();
});
