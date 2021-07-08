django.jQuery(function($) {
	'use strict';
	var $selectIconFont = $('#id_icon_font'),
	    $symbol = $('#id_menu_symbol'),
	    $box = $symbol.closest('.field-menu_symbol');

	$selectIconFont.change(fontChanged);
	fontChanged();
	$('label[for="id_menu_symbol"]').remove();
	$box.removeClass('hidden');
	$box.on('click', 'ul.font-family li', selectIcon);

	function fontChanged() {
		var link;
		if ($selectIconFont.length === 0)
			return;
		link = {
			id: "id_iconfont_link",
			rel: "stylesheet",
			type: "text/css",
			href: django.cascade.iconfont_stylesheet_urls[$selectIconFont.val()]
		};
		$('#id_iconfont_link').remove();
		$("<link/>", link).appendTo("head");

		if ($selectIconFont.val()) {
			$.get(django.cascade.fetch_fonticons_url + $selectIconFont.val()).done(renderIcons);
		}
	}

	function selectIcon() {
		$box.find('ul.font-family li.selected').removeClass('selected');
		$(this).addClass('selected');
		$symbol.val($(this).attr('title'));
	}

	function renderIcons(response) {
		var css_prefix_text = response.css_prefix_text;
		$box.find('label[for="query"], h2, ul').remove();
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
	}
});
