# Migrating towards Bootstrap-4

Currently I'am refactoring **djangocms-cascade**, adding support for Bootstrap-4. This is not as
easy as one might expect, because of the way Bootstrap-4 handles the width of columns. Remember,
in Bootstrap-3 the width of each column was predictable. With the advent of auto-columns in
Bootstrap-4, this isn't possible anymore.


## Why does this matter?

One of **djangocms-cascade**'s great features is, that it always keeps track of the column
width for each available breakpoint. This is important, so that responsive images can be
thumbnailed to fit exactly into a given column and hence save bandwidth. Therefore in Bootstrap-3,
Cascade rendered images with up to 8 thumbnails in different sizes. From these the browser then is
able to choose that one, which best fits into the given viewport.

This in modern HTML is handled by the `<img ...>` element itself, using the attributes `sizes`
together with `srcset`. The `<picture>` element, uses the children elements `<source ...>`.


## In Bootstrap-4, this approach doesn't work anymore 

In Bootstrap-4, containers use the flexbox model rather than floating divs. This allows the use
of columns with equally distributed width, in addition to the fixed sized columns we already know.
Therefore the widths of the columns can only be calculated, if we know how their siblings are made
up. Therefore the existing approach to determine the widths of columns used by **djangocms-cascade**
doesn't work anymore.

Therefore uses another approach.

Instead of keeping track on the widths of containers, rows and columns, version 0.17 of
**djangocms-cascade** calculates this only for images.


In the meantime I tried to come up with alternative ideas for my problem with computing image
widths.
As you know, in Cascade-BS3, for each image 4 different (8 for retina) widths are computed and
delivered with their <img srcset="...">. This was relatively easy, since in BS-3 we had to deal
with pixels and the widths of columns was determinable. As much as I bump my head against the table,
I can't find a generic solution for BS-4. Consider columns such as `<div class="col-auto">some content</div>`,
how do you determine the maximum width in order to thumbnail the image and compute the srcset-s?
But even without auto-width columns, it gets really difficult to get all edge cases.
