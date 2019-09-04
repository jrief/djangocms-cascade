django.jQuery(function($) {
	'use strict';
	var picker = null, AColorPicker = window.AColorPicker;

	function checkboxChanged(checkboxInput) {
		var $rgbaInput = $(checkboxInput).siblings('input.cascade-rgba');
		var $colorInput = $(checkboxInput).siblings('input[type="color"]');
		if (checkboxInput.checked || checkboxInput.disabled) {
			$rgbaInput.addClass('disabled');
			if (!AColorPicker) {
				$colorInput.addClass('disabled');
				}
		} else {
			$rgbaInput.removeClass('disabled');
			if (!AColorPicker) {
				$colorInput.removeClass('disabled');
				}
		}
	}

	if (AColorPicker) {
		$('.cascade-colorpicker > input.cascade-rgba').on('click', function(evt) {
			var $this = $(this);
			var $colorInput = $this.siblings('input[type="color"]');
			var options = {color: $this.val(), showAlpha: true};
			if (picker) {
				picker.destroy();
			}
			if ($this.hasClass('disabled')) {
				$this.blur();
			} else {
				picker = AColorPicker.createPicker($this.parent(), options);
			 	$('.a-color-picker input[type="number"]').css("cssText", "padding: 2px 0 !important;");
				picker.on('change', function(picker, color) {
					$colorInput.val(AColorPicker.parseColor(color, 'hex'));
					$this.val(color);
				});
			}
			evt.preventDefault();
		});
		$('.cascade-colorpicker > input[type="color"]').on('click', function(evt) {
			evt.preventDefault();
		});
	} else {
		$('.cascade-colorpicker > input.cascade-rgba').on('focus', function(evt) {
			var $this = $(this);
			$this.blur();
			if (!$this.hasClass('disabled')) {
				$this.siblings('input[type="color"]').trigger('click');
			}
		});
		$('.cascade-colorpicker > input[type="color"]').on('change', function(evt) {
			var $rgbaInput = $(this).siblings('input.cascade-rgba');
			$rgbaInput.val($(this).val());
		});
	}

	$(document).on('click', function(evt) {
		if (picker && $(evt.target).closest('.cascade-colorpicker').length === 0) {
			picker.destroy();
			picker = null;
		}
	});

	$('.cascade-colorpicker > input[type="checkbox"]').on('change', function(evt) {
		checkboxChanged(evt.target);
	});
	$.each($('.cascade-colorpicker > input[type="checkbox"]'), function() {
		checkboxChanged(this);
	});
});
