django.jQuery(function($) {
    'use strict';
    $.getScript("/static/node_modules/a-color-picker/dist/acolorpicker.js", function() {});

    function color_selector(data, id_picker) {
        var bools = {};
        data = $(data);
        if (data) {
            bools[data] = true;
            var $colordefault = data.val();
            data.parent().append('<span id="thumb' + id_picker + '" style="background-color:' + data.val() + '; position: absolute; top: 5px;  left: 5px; width: 18px; height:18px;" ></span>');
            data.on('click', function() {
                if (bools[data]) {
                    data.parent().append('<div id="' + id_picker + '"  acp-color="' + data.val() + '"  acp-show-rgb="yes" acp-show-hsl="yes" acp-show-hex="yes" acp-show-alpha></div>');
                    data.parent().append('<input id="undo_' + id_picker + '"  type="button" value="Undo">');
                    AColorPicker.from('#' + id_picker).on('change', (picker, color) => {
                        data.val(picker.color);
                        $('#thumb' + id_picker).css("background-color", data.val())
                    });
                    bools[data] = false;
                    $('#undo_' + id_picker).on('click', function() {
                        data.val($colordefault);
                        $('#' + id_picker).detach();
                        $('#thumb' + id_picker).css("background-color", data.val());
                        $('#undo_' + id_picker).detach();
                        bools[data] = true;
                    });
                } else {
                    $('#' + id_picker).detach();
                    $('#undo_' + id_picker).detach();
                    bools[data] = true;
                }
            });
        }
    };
    color_selector('#id_glossary_extra_inline_styles\\:color_color', 'id_picker_color');
    color_selector('#id_glossary_extra_inline_styles\\:background-color_color', 'id_picker_backgroundcolor');
});
