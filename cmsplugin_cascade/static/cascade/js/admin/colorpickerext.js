django.jQuery(function($) {
    'use strict';
    $.getScript("/static/node_modules/a-color-picker/dist/acolorpicker.js", function() {});

    function color_selector(id_glossary) {
        var is_not_open = true;
        var $colordefault = id_glossary.val();
        var parent = id_glossary.parent();
        parent.append('<span class="thumb_color_picker" style="background-color:' + id_glossary.val() + '; position: absolute; top: 5px;  left: 5px; width: 18px; height:18px; border: 1px solid;" ></span>');
        id_glossary.add('.thumb_color_picker').on('click', function() {
            if (is_not_open) {
                parent.append('<div class="acolor_picker"  acp-color="' + id_glossary.val() + '"  acp-show-rgb="no" acp-show-hsl="yes" acp-show-hex="yes" acp-show-alpha></div>');
                parent.append('<input class="undo_color_picker"  type="button" value="Undo">');
                var cp = id_glossary.parent().find('.acolor_picker');
                var thumb_cp = parent.find('.thumb_color_picker');
                AColorPicker.from(cp).on('change', (picker, color) => {
                    id_glossary.val(picker.color);
                    thumb_cp.css("background-color", id_glossary.val())
                });
                is_not_open = false;
                var undo_cp = id_glossary.parent().find('.undo_color_picker')
                undo_cp.on('click', function() {
                    id_glossary.val($colordefault);
                    cp.detach();
                    thumb_cp.css("background-color", id_glossary.val());
                    undo_cp.detach();
                    is_not_open = true;
                });
            } else {
                id_glossary.parent().find('.acolor_picker').detach();
                id_glossary.parent().find('.undo_color_picker').detach();
                is_not_open = true;
            }
        });
    };
    $('.color_picker input').each(function() {
        color_selector($(this));
    });

});
