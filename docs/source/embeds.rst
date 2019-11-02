================
Embedding Videos
================

Staring in 0.18, it is possible to embedd a video inside a Bootstrap column. Each video provider
offers a distinct set of parameters to configure how their videos are broadcasted. Therefore,
**djangocms-cascade** offers a plugin for each of them.


YouTube
=======

When adding a plugin to a column, select the **YouTube**. The YouTube URL is found by clicking on
the **SHARE** button, then copying and pasting it into the URL field in the editor. Select the
right aspect ratio, otherwise you end up with right and left edged cut away.

For all other options, the YouTube plugin editor offers, consult the `IFrame Player API`_.

.. _IFrame Player API: https://developers.google.com/youtube/player_parameters


Vimeo
=====

Currently no plugin for Vimeo has been written yet. It would however be quite easy to do so.
