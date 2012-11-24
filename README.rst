========
Overview
========


This product aims at enabling you to self-host your videos efficiently,
not bogging your Plone server down with actual video handling
(conversion etc.). Instead, you simply generate small text files telling
Plone where to actually find the videos, banner images etc. - see below.


This product adds a "Video" content type with the following features:

 * For each video, some metadata, like author and date of recording,
   are collected.
 * The videos themselves are served off the bare file system. The
   product itself contains only sort of pointers to video files.
 * The user should be able to view the file in a number of formats,
   resolutions etc., and to download the videos.
 * Conversion of videos from one format to another is outside the
   scope of this product.
 * Access control to the actual video files is outside the scope of
   this product. Only the metadata, as defined in this product's
   schema, will be workflowed.
 * The product will determine, at run time, the available formats for
   a given video, and offer the user only these for viewing or download.
 * The product aims to offer access to said videos for as many
   client environments as possible.
 * The product makes use of flowplayer (www.flowplayer.org).



Structure of a metadata file
----------------------------

Each video requires a "metadata" file which adheres to the following
structure:


    * First line:
      Column 1: "thumbnail"
      Column 2: filename for the thumbnail, if any
    * Second line:
      Column 1: "playing time"
      Column 2: time spec (HH:MM:SS)
    * Third line:
      Column 1: "selected"
      Column 2: file name of the video that is to be played in the browser
    * Fourth line:
      Column 1: "default size"
      Column 2: size specification in width x height, eg. "500x300"
    * Remaining lines:
      Column 1: resolution and format, eg. "640x480, OGV"
      Column 2: complete file name (without directories)


You generate these files out-of-band in accord with your requirements for
video hosting.
