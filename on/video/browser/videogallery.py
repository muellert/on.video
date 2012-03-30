
# gallery view for folders containing videos

# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

"""
Folder view that enables the display of videos like in a photo
gallery.

These are the differences to the normal gallery view of folders:

 * Videos are displayed using their summary view. May be
   generalized later.

 * Contained folders are searched for sub-galleries, and a
   thumbnail and description about the collection is being
   displayed.

 * Next-Previous navigation is generally enabled.

 * If possible, creating sub-folders should inherit this gallery
   view from their parent folder, so that contained folders are
   automatically also galleries by default.


Open question: How to revert the display settings for folders
on uninstallation of the product?

"""

from zope.interface import Interface
from five import grok

from Products.ATContentTypes.interface import IATFolder

from Products.CMFPlone.PloneBatch import Batch
from plone.memoize.instance import memoize

from on.video import _

from on.video.video import ViewThumbnail



class FolderItems(object):
    """Collect attributes for folder entries."""
    def __init__(self, data, datatype, start):
        self.data = data
        self.datatype = datatype
        self.filetype = self.calculateFileType(url)
        self.start = start

def countFolderItems(folder):
    """Filter the given list of folder contents for those elements
       that are intended to be shown in the video gallery, and
       count them.
       Return a pair (folders, videos).
    """
    folderlisting = folder.folderlistingFolderContents()
    counts = { 'Folder': 0, 'on.video.Video': 0 }
    for item in folderlisting:
        if not item.portal_type in ('Folder', 'on.video.Video'):
            continue
        counts[item.portal_type] += 1
    return (counts['Folder'], counts['on.video.Video'])


def genSmallView(item, request = None):
    """Turn a content item into a dictionary. We only need specific
       information, depending on type.
    """
    result = dict(portaltype=item.portal_type, id=item.id, title=item.title)
    result['banner'] = '/++resource++on.video/nothumbnail.png'
    if item.portal_type == 'Folder':
        (folders, videos) = countFolderItems(item)
        result['sub_folder'] = folders
        result['sub_videos'] = videos
        # assumption: the image is an ArcheTypes image
        if 'bannerimage' in item.keys():
            result['thumb'] = '%s/bannerimage/image' % item.id
        # print "genSmallView(): item= ", item
        result['title'] = item.title[0:20]
    elif item.portal_type == 'on.video.Video':
        result['sub_folder'] = None
        result['sub_videos'] = None
        # this information is not accessible from here:
        vtn = ViewThumbnail(item, request)
        result['playingtime'] = vtn.playing_time
        result['thumb'] = vtn.thumbnail()
        result['title'] = vtn.title()
    # print "genSmallView(): result= ", result
    return result


class VideoGallery(grok.View):
    """Default view, gallery style, for a video folder.
    """
    grok.context(IATFolder)
    grok.require('zope2.View')

    @memoize
    def getFolderContents(self):
        """Filter the folder contents for those elements that are
           intended to be shown in the video gallery.
        """
        return [ item for item in self.context.folderlistingFolderContents() if
                      item.portal_type in ('Folder', 'on.video.Video', 'Image') ]

    @memoize
    def update(self):
        """Called before rendering the template for this view.
        """
        fl = self.getFolderContents()
        b_start = int(self.context.REQUEST.get('b_start', 0))
        self.contents = Batch([ genSmallView(item, self.request) for item in fl ], size=15, start=b_start)
    
        # print "VideoGallery.update(): contents = ", self.contents
        # import pdb; pdb.set_trace()

    @memoize
    def xxxvideoListing(self):
        """Get all child videos and video folders in this folder.
        """
        folder = self.context
        items = folder.keys()
