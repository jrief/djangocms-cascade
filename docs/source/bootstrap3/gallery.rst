.. _bootstrap3/gallery:

=======
Gallery
=======

A gallery is a collection of images displayed as a group. Since it normally consists of many similar
images, **djangocms-cascade** does not require to use child plugins for each image. Instead they
can be added directly to the **Bootstrap Gallery Plugin**. Here, **djangocms-cascade** uses a
special model, named :class:`cmsplugin_cascade.models.InlineCascadeElement` which also uses a JSON
field to store it's payload. It thus can be configured to accept any kind of data, just as it's
counterpart :class:`cmsplugin_cascade.models.CascadeElement` does.

Since plugin editors are based on Django's admin backend, the Gallery Plugin uses the Stacked Inline
formset to manage it's children. If **django-admin-sortable2** is installed, the entries in the
plugin can even be sorted using drag and drop.
