django.jQuery(function($) {
	'use strict';

	// create class handling the client-side part of FontIconPlugin
	var self, FontIcon, base_plugins = eval(django.cascade.base_plugins),
	    $selectIconFont = $('#id_glossary_icon_font'),
	    $content = $('#id_glossary_content'),
	    $box = $content.closest('.glossary-box');

	FontIcon = ring.create(base_plugins, {
		constructor: function() {
			self = this;
			this.$super();

			// install event handlers
			$selectIconFont.on('change', self.fontChanged);
			$box.on('click', 'ul.font-family li', self.selectIcon);

			// set defaults
			this.refreshChangeForm();
		},
		fontChanged: function () {
			var link = {
				id: "id_iconfont_link",
				rel: "stylesheet",
				type: "text/css",
				href: django.cascade.iconfont_stylesheet_urls[$selectIconFont.val()]
			};
			$('#id_iconfont_link').remove();
			$("<link/>", link).appendTo("head");

			$('#id_iconfont_families').remove();
			$.get(django.cascade.fetch_fonticons_url + $selectIconFont.val()).done(self.renderIcons);
		},
		selectIcon: function() {
			$box.find('ul.font-family li.selected').removeClass('selected');
			$(this).addClass('selected');
			$content.val($(this).attr('title'));
		},
		renderIcons: function(response) {
			var css_prefix_text = response.css_prefix_text || 'icon-';
			$box.find('h2, ul').remove();
			$.each(response.families, function(key, icons) {
				var lis = [];
				$content.before('<h2>' + key + '</h2>');
				$.each(icons, function(idx, icon) {
					lis.push('<li title="' + icon + '"><i class="' + css_prefix_text + icon + '"></i></li>');
				});
				$content.before('<ul class="font-family">' + lis.join('') + '</ul>');
			});

			// mark selected icon
			$box.find('ul.font-family li.selected').removeClass('selected');
			$box.find('ul.font-family li[title=' + $content.val() + ']').addClass('selected');
		},
		refreshChangeForm: function() {
			this.fontChanged();
			this.$super && this.$super();
		}

	});

	new FontIcon();
});
