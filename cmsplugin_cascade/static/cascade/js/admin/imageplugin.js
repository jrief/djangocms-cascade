
django.jQuery(function($) {
	'use strict';
	var breakpoints = ['xs', 'sm', 'md', 'lg'];

	var ImagePlugin = ring.create([django.cascade.LinkPluginBase, django.cascade.SharableGlossary], {
		constructor: function() {
			var self = this, $image_responsive = $('#id_glossary_image-shapes_0');
			this.$super();

			// be more intuitive, reorganize layout by moving radio boxes for 'Link Target'
			$('.glossary-widget .glossary_target').before($('.form-row.field-link_type'));
			// move the select box for Shared Glossary just before 'Image Shapes'
			$('.glossary-widget .glossary_image-shapes').before($('.form-row.field-shared_glossary'));

			// install event handlers
			$image_responsive.change(function(evt) {
				self.toggleResponsive(evt.target.checked);
			});
			this.toggleResponsive($image_responsive.prop('checked'));
		},
		toggleSharedGlossary: function($option) {
			var glossary = $option.data('glossary');

			if (glossary) {
				$('#id_glossary_image-shapes input').each(function(idx, elem) {
					$(elem).prop('checked', glossary['image-shapes'].indexOf($(elem).val()) >= 0);
					$(elem).prop('disabled', 'disabled');
				});
				this.toggleResponsive($('#id_glossary_image-shapes_0').prop('checked'));
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
		},
		toggleResponsive: function(checked) {
			var $image_width_responsive = $('.glossary-widget .glossary_image-width-responsive').parent(),
				$image_width_fixed = $('.glossary-widget .glossary_image-width-fixed').parent(),
				$image_heights_responsive = $('.glossary-widget .glossary_image-heights-responsive').parent(),
				$image_height_fixed = $('.glossary-widget .glossary_image-height-fixed').parent();
			
			// if checkbox Image Shapes: Responsive is active, show adaptive width and heights
			if (checked) {
				$image_width_responsive.show();
				$image_width_fixed.hide();
				$image_heights_responsive.show();
				$image_height_fixed.hide();
			} else {
				$image_width_responsive.hide();
				$image_width_fixed.show();
				$image_heights_responsive.hide();
				$image_height_fixed.show();
			}
		}
	});

	new ImagePlugin();
});
