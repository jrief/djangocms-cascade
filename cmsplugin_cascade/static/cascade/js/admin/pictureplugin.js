
django.jQuery(function($) {
	'use strict';
	var breakpoints = ['xs', 'sm', 'md', 'lg'];

	var PicturePlugin = ring.create([django.cascade.LinkPluginBase, django.cascade.SharableGlossary], {
		constructor: function() {
			var self = this, $image_responsive = $('#id_glossary_image-shapes_0');
			this.$super();

			// be more intuitive, reorganize layout by moving radio boxes for 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));
		},
		toggleSharedGlossary: function($option) {
			var glossary = $option.data('glossary');

			if (glossary) {
				$('#id_glossary_image-shapes input').each(function(idx, elem) {
					$(elem).prop('checked', glossary['image-shapes'].indexOf($(elem).val()) >= 0);
					$(elem).prop('disabled', 'disabled');
				});
				$.each(breakpoints, function(idx, bp) {
					$('#id_glossary_responsive-heights[name$=' + bp + ']').val(glossary['responsive-heights'][bp]).prop('disabled', 'disabled');
				});
				$('#id_glossary_image-size[name$="width"]').val(glossary['image-size']['width']).prop('disabled', 'disabled');
				$('#id_glossary_image-size[name$="height"]').val(glossary['image-size']['height']).prop('disabled', 'disabled');
				$('#id_glossary_resize-options input').each(function(idx, elem) {
					$(elem).prop('checked', glossary['resize-options'].indexOf($(elem).val()) >= 0);
					$(elem).prop('disabled', 'disabled');
				});
			} else {
				$('#id_glossary_image-shapes input').prop('disabled', '');
				$.each(breakpoints, function(idx, bp) {
					$('#id_glossary_responsive-heights[name$=' + bp + ']').prop('disabled', '');
				});
				$('#id_glossary_image-size[name$="width"]').prop('disabled', '');
				$('#id_glossary_image-size[name$="height"]').prop('disabled', '');
				$('#id_glossary_resize-options input').prop('disabled', '');
			}
			this.$super($option);
		}
	});

	new PicturePlugin();
});
