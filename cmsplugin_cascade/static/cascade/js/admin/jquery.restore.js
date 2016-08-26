// re-add jQuery to global namespace since otherwise the Select2Widget does not work
window['jQuery'] = jQuery || django.jQuery;