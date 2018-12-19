django.jQuery(function($) {
    'use strict';

    function color_selector(id_glossary, id_picker) {
        var data = $(id_glossary);
        var thumb = 'thumb_' + id_picker;
        if (data) {

            if ($('#' + id_picker).length == '0') {
                data.parent().append('<input id="' + id_picker + '" type="color" style="display:none;opacity:0;position:absolute;"/>');
                data.parent().append('<span id="' + thumb + '" style="background-color:' + data.val() + '; position: absolute; top: 5px;  left: 5px; width: 18px; height:18px; border: 1px solid;" ></span>');
            }
            data.add("#" + thumb).on('click', function() {

                $('#' + id_picker).on('change', $('#' + id_picker), function() {
                    $('#' + thumb).css('background-color', $('#' + id_picker).val());
                    data.val($('#' + id_picker).val());
                });
                $('#' + id_picker).trigger('click');
            });
        };
    };
    
    color_selector('#id_glossary_extra_inline_styles\\:color_color', 'id_picker_color');
    color_selector('#id_glossary_extra_inline_styles\\:background-color_color', 'id_picker_backgroundcolor');
});
