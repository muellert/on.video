Introduction
============

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

