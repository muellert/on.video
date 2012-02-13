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

#from zope import schema
#from plone.directives import form
#from plone.namedfile.field import NamedBlobImage
from plone.memoize.instance import memoize

from on.video import _

#grok.templatedir('templates')



"""
>>> fl = x.folderlistingFolderContents()
>>> fl
[<Item at /01/mnt/Plone/x/somemovie>, <Item at /01/mnt/Plone/x/movie2>, <ATFolder at /01/mnt/Plone/x/blubb>, <Item at /01/mnt/Plone/x/video-in-folder>, <Item at /01/mnt/Plone/x/anothervideo>]
>>> fl[2].getTypeInfo().title
'Folder'
>>> fl[1].getTypeInfo().title
'Video'
>>>

"""

class FolderItems(object):
    """Collect attributes for folder entries."""
    def __init__(self, data, datatype):
        self.data = data
        self.datatype = datatype
        self.filetype = self.calculateFileType(url)


def genSmallView(item):
    """Turn a content item into a dictionary. We only need specific
       information, depending on type.
    """
    result = dict(portaltype=item.portal_type, id=item.id, title=item.title)
    
    return result

class VideoGallery(grok.View):
    """Default view, gallery style, for a video folder.
    """
    grok.context(IATFolder)
    grok.require('zope2.View')
    #grok.name('view') - redundant

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
        self.contents = [ genSmallView(item) for item in fl ]
        result = []
	"""
        for item in fl:
            #d = dict(item=item[0], type_=item[1])
            result.append(None)
	"""

    @memoize
    def videoListing(self):
        """Get all child videos and video folders in this folder.
        """
        folder = self.context
        items = folder.keys()
