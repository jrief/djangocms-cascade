django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of plugins inheriting from IconPluginMixin
	var $symbol = $('#id_glossary_symbol'),
	    $box = $symbol.closest('.glossary-box');

	django.cascade.IconPluginMixin = ring.create(eval(django.cascade.ring_plugin_bases.IconPluginMixin), {
		constructor: function() {
			this.$super();
			this.renderIcons();

			// install event handlers
			$box.on('click', 'ul.font-family li', this.selectIcon);
		},
		selectIcon: function() {
			$box.find('ul.font-family li.selected').removeClass('selected');
			$(this).addClass('selected');
			$symbol.val($(this).attr('title'));
		},
		renderIcons: function() {
			var config_data, css_prefix_text;
			try {
				config_data = JSON.parse($("#cascade_iconfont_config_data").text());
			} catch (parse_error) {
				return;
			}
			css_prefix_text = config_data.css_prefix_text || 'icon-';
			$box.find('h2, ul').remove();
			$.each(config_data.families, function(key, icons) {
				var lis = [];
				$symbol.before('<h2>' + key + '</h2>');
				$symbol.before('<label for="query">Search Icon:</label><input id="fonticon_search_query" type="text" name="query">');
				$.each(icons, function(idx, icon) {
					lis.push('<li title="' + icon + '"><i class="' + css_prefix_text + icon + '"></i></li>');
				});
				$symbol.before('<ul id="fonticon_symbols" class="font-family">' + lis.join('') + '</ul>');
				$('#fonticon_search_query').bind('keyup paste', function(event) {
					var fonticon_symbols = $('#fonticon_symbols').find('li'), re;
					if (event.target.value) {
						re = new RegExp(event.target.value, 'i');
						fonticon_symbols.each(function() {
							var cssClass = $(this).children('i').attr('class');
							if (cssClass.substring(css_prefix_text.length).match(re)) {
								$(this).show();
							} else {
								$(this).hide();
							}
						})
					} else {
						fonticon_symbols.show();
					}

				});
			});

			// mark selected icon
			$box.find('ul.font-family li.selected').removeClass('selected');
			if ($symbol.val()) {
				$box.find('ul.font-family li[title=' + $symbol.val() + ']').addClass('selected');
			}
		}
	});
});
