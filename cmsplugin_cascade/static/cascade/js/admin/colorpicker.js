django.jQuery(function($) {
    'use strict';

    function color_selector(data, id_picker) {
        var bools = {};
        data = $(data);
        if (data) {
            var $colordefault = data.val();
            if ($('#' + id_picker).length == '0') {
                data.parent().append('<input id="' + id_picker + '" type="color" style="opacity:0;position:absolute;"/>');
                data.parent().append('<span id="thumb' + id_picker + '" style="background-color:' + data.val() + '; position: absolute; top: 5px;  left: 5px; width: 18px; height:18px;" >' +
                    '</span>');
            }
            data.on('click', function() {
                if (bools[data] = 'undefined') {
                    $('#' + id_picker).on('change', $('#' + id_picker), function() {
                        $('#thumb' + id_picker).css('background-color', $('#' + id_picker).val());
                        data.val($('#' + id_picker).val());
                    });
                    $('#' + id_picker).trigger('click');
                };
            });
        };
    };
    color_selector('#id_glossary_extra_inline_styles\\:color_color', 'id_picker_color');
    color_selector('#id_glossary_extra_inline_styles\\:background-color_color', 'id_picker_backgroundcolor');
});
