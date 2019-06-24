django.jQuery(function($) {
	'use strict';
	var $colorElem = $('.cascade-color-picker > input[type="color"]');
	var $checkboxElem = $('.cascade-color-picker > input[type="checkbox"]');
	var picker = null, AColorPicker = window.AColorPicker;

	function colorWidgetChanged(checkboxInput) {
		var $colorInput = $(checkboxInput).siblings('input[type="color"]');
		$colorInput.prop('disabled', checkboxInput.checked || checkboxInput.disabled);
	}

	if (AColorPicker) {
		$colorElem.on('click', function(evt) {
			var $this = $(this);
			var $rgbaField = $this.siblings('input[type="hidden"]');
			var options = {color: $rgbaField.val(), showAlpha: $rgbaField.data('with_alpha')};
			if (picker) {
				picker.destroy();
			}
			picker = AColorPicker.createPicker($this.parent(), options);
			picker.on('change', function(picker, color) {
				$this.val(AColorPicker.parseColor(color, 'hex'));
				$rgbaField.val(color);
			});
			evt.preventDefault();
		});
	}

	$(document).on('click', function(evt) {
		if (picker && $(evt.target).closest('.cascade-color-picker').length === 0) {
			picker.destroy();
			picker = null;
		}
	});

	if ($checkboxElem) {
		$checkboxElem.on('change', function(evt) {
			colorWidgetChanged(evt.target);
		});
		$.each($checkboxElem, function() {
			colorWidgetChanged(this);
		});
	}
});
