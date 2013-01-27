
# gallery view for folders containing videos

# (c) 2012-2013 oeko.net
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

from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from plone.app.contentlisting import catalog
from on.video import _

from on.video.video import ViewThumbnail


class FolderItems(object):
    """Collect attributes for folder entries."""
    def __init__(self, data, datatype, start):
        self.data = data
        self.datatype = datatype
        self.filetype = self.calculateFileType(url)
        self.start = start

def XXXXcountFolderItems(item):
    """item count to be shown in a folder / collection summary view
       Return a pair (folders, videos).
    """
    counts = { 'Folder': 0, 'on.video.Video': 0 }
    #import pdb; pdb.set_trace()

    if item.getPortalTypeName() == 'Folder':
        # import pdb; pdb.set_trace()
        try:
            flist = item.folderlistingFolderContents()
        except:
            obj = item._brain.getObject()
            flist = obj.folderlistingFolderContents()
    if item.getPortalTypeName() == 'Collection':
        catalog = getToolByName(self, 'portal_catalog')
        flist = self.context.results(batch=False)

    for item in flist:
        if not item.portal_type in ('Folder', 'on.video.Video'):
            continue
        counts[item.portal_type] += 1
        
    return (counts['Folder'], counts['on.video.Video'])


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
        g = 0
        v = 0
        if item.portal_type == 'Folder':
            (g, v) = countFolderItems(item)
        counts['Folder'] += g
        counts['on.video.Video'] += v
    return (counts['Folder'], counts['on.video.Video'])

def shorttitle(title):
    """shorten titles for gallery view"""
    if len(title) > 50:
        tshort = title[:47] + "..."
    else: tshort = title
    tdict = {'short': tshort, 'long': title}
    return tdict


def genSmallView(item, request = None):
    """Turn a content item into a dictionary. We only need specific
       information, depending on type.
    """
    result = dict(portaltype=item.portal_type, id=item.id, title=item.title)
    result['banner'] = '/++resource++on.video/nothumbnail.png'
    # import pdb; pdb.set_trace()
    try: # Are we are in a collection? 
        result['path'] =item.getPath()
    except: # Or in a Folder?
        result['path'] =item.absolute_url()
    
    if item.portal_type == 'Folder':
        (folders, videos) = countFolderItems(item)
        result['sub_folder'] = folders
        result['sub_videos'] = videos
        # assumption: the image is an ArcheTypes image
        if 'bannerimage' in item.keys():
            result['thumb'] = '%s/bannerimage/image' % item.id
        titles = shorttitle(item.title)
        result['title'] = titles['short']
        result['longtitle'] = titles['long']

    elif item.portal_type == 'on.video.Video':
        result['sub_folder'] = None
        result['sub_videos'] = None
        # this information is not accessible from here:
        vtn = ViewThumbnail(item, request)
        result['playingtime'] = vtn.playing_time
        result['thumb'] = vtn.thumbnail()
        titles = shorttitle(item.title)
        result['title'] = titles['short']
        result['director'] = item.director or ""
        result['longtitle'] = titles['long']

    elif item.portal_type == 'Image':
        result['sub_folder'] = None
        result['sub_videos'] = None
        result['thumb'] = '%s/image' % item.id
        titles = shorttitle(item.title)
        result['title'] = titles['short']
        result['longtitle'] = titles['long']
    else:
        raise ValueError, "item %s is an object of an illegal type." % str(item)
    # print result
    return result


class VideoGallery(grok.View):
    """Default view, gallery style, for a video folder.
    """
    grok.context(Interface)
    grok.require('zope2.View')

    #@memoize
    def getFolderContents(self):
        """Filter the folder contents for those elements that are
           intended to be shown in the video gallery.
        """
        if self.context.portal_type == 'Folder':
            contents = [ item for item in self.context.folderlistingFolderContents() if \
                         item.portal_type in ('Folder', 'on.video.Video', 'Image')
                         and item is not None]
        if self.context.portal_type == 'Collection':
            """partly taken from plone.app.collection"""
            catalog = getToolByName(self, 'portal_catalog')
            results = self.context.results(batch=False)

            contents = [ item for item in results if \
                         item.portal_type in ('Folder', 'on.video.Video', 'Image')
                         and item is not None]
            #print "VideoGallery(%s) getFolderContens: contents = %s" % (str(self), str(contents))
        return contents

    #@memoize
    def update(self):
        """Called before rendering the template for this view.
        """
        fl = [ x for x in self.getFolderContents() if x.id != 'bannerimage' ]
        b_start = int(self.context.REQUEST.get('b_start', 0))
        #print "VideoGallery() update: b_start = %d, fl = %s" % (b_start, str(fl))
        self.contents = Batch([ genSmallView(item, self.request) for item in fl ], size=12, start=b_start)
