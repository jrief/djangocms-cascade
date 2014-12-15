
django.jQuery(function($) {
	'use strict';

	var PicturePlugin, base_plugins = eval(django.cascade.base_plugins);

	// create class handling the client-side part of PicturePlugin
	PicturePlugin = ring.create(base_plugins, {});
	new PicturePlugin();
});
