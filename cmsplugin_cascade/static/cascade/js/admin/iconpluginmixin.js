django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of plugins inheriting from IconPluginMixin
	var $selectIconFont = $('#id_icon_font'),
	    $symbol = $('#id_symbol'),
	    $box = $symbol.closest('.form-row.field-symbol');

	django.cascade.IconPluginMixin = ring.create(eval(django.cascade.ring_plugin_bases.IconPluginMixin), {
		constructor: function() {
			var self = this;
			if ($selectIconFont.length === 0)
				return;
			this.$super();

			// install event handlers
			$selectIconFont.on('change', function() {
				self.fontChanged();
			});
			$box.removeClass('hidden');
			$box.on('click', 'ul.font-family li', this.selectIcon);

			// set defaults
			this.refreshChangeForm();
		},
		fontChanged: function() {
			var link;
			if ($selectIconFont.length === 0)
				return;
			$('#id_iconfont_link').remove();
			if ($selectIconFont.val()) {
				link = {
					id: "id_iconfont_link",
					rel: "stylesheet",
					type: "text/css",
					href: django.cascade.iconfont_stylesheet_urls[$selectIconFont.val()]
				};
				$("<link/>", link).appendTo("head");

				$('.form-row.field-symbol').show();
				$.get(django.cascade.fetch_fonticons_url + $selectIconFont.val()).done(this.renderIcons);
			} else {
				$('.form-row.field-symbol').hide();
			}
		},
		selectIcon: function() {
			$box.find('ul.font-family li.selected').removeClass('selected');
			$(this).addClass('selected');
			$symbol.val($(this).attr('title'));
		},
		renderIcons: function(response) {
			var css_prefix_text = response.css_prefix_text;
			$box.find('label[for="query"], h2, ul:not(.errorlist)').remove();
			$('#fonticon_search_query').remove();
			$.each(response.families, function(key, icons) {
				var lis = [];
				$symbol.before('<h2>' + key + '</h2>');
				$symbol.before('<label for="query">Search Icon:</label><input id="fonticon_search_query" type="text" name="query">');
				$.each(icons, function(idx, icon) {
					lis.push('<li title="' + icon + '"><i class="' + css_prefix_text + icon + '"></i></li>');
				});
				$symbol.before('<ul id="fonticon_symbols" class="font-family">' + lis.join('') + '</ul>');
				$('#fonticon_search_query').on('keyup paste', function(event) {
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
		},
		refreshChangeForm: function() {
			this.fontChanged();
			this.$super && this.$super();
		}
	});
});
