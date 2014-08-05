
django.jQuery(function($) {
	'use strict';

	var PicturePlugin = ring.create([django.cascade.LinkPluginBase, django.cascade.SharableGlossary], {
		constructor: function() {
			var self = this, $image_responsive = $('#id_glossary_image-shapes_0');
			this.$super();

			// be more intuitive, reorganize layout by moving radio boxes for 'Link Target'
			$('.glossary-widget.glossary_target').before($('.form-row.field-link_type'));
			// move the select box for Shared Glossary just before 'Image Shapes'
			$('.glossary-widget.glossary_image-shapes').before($('.form-row.field-shared_glossary'));

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
				$('#id_glossary_responsive-height').val(glossary['responsive-height']).prop('disabled', 'disabled');
				$('#id_glossary_image-size[name$="width"]').val(glossary['image-size']['width']).prop('disabled', 'disabled');
				$('#id_glossary_image-size[name$="height"]').val(glossary['image-size']['height']).prop('disabled', 'disabled');
				$('#id_glossary_resize-options input').each(function(idx, elem) {
					$(elem).prop('checked', glossary['resize-options'].indexOf($(elem).val()) >= 0);
					$(elem).prop('disabled', 'disabled');
				});
			} else {
				$('#id_glossary_image-shapes input').prop('disabled', '');
				$('#id_glossary_responsive-height').prop('disabled', '');
				$('#id_glossary_image-size[name$="width"]').prop('disabled', '');
				$('#id_glossary_image-size[name$="height"]').prop('disabled', '');
				$('#id_glossary_resize-options input').prop('disabled', '');
			}
			this.$super($option);
		},
		toggleResponsive: function(checked) {
			var $glossary_responsive = $('.glossary-widget.glossary_responsive-height'),
				$glossary_static = $('.glossary-widget.glossary_image-size');

			// if checkbox Image Shapes: Responsive is active, replace 'Image Size' against 'Container Height'
			if (checked) {
				$glossary_responsive.show();
				$glossary_static.hide();
			} else {
				$glossary_responsive.hide();
				$glossary_static.show();
			}
		}
	});

	new PicturePlugin();
});
