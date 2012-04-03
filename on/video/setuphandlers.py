from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName


site = None
wftool = None

def createFolder(container, folderid, foldername, **kw):
    """Create a folder with the given properties and publish it"""
    container.invokeFactory("Folder", id=folderid, title=foldername)
    newfolder = container[folderid]
    if "description" in kw.keys():
        newfolder.setDescription(kw['description'])
    newfolder.setOrdering('unordered')
    newfolder.unmarkCreationFlag()
    wftool.doActionFor(newfolder, 'publish')
    return newfolder


def setupVideoResources(context):
    """Set up default content and other site-specific stuff.
    """

    if context.readDataFile('on.video-setup.txt') is None:
        return

    global site, wftool
    
    site = context.getSite()
    wftool = getToolByName(site, "portal_workflow")
    # existing = site.keys()
    
    if 'Videoresources' not in site.keys():
    
        descr = "This folder contains one Subfolder 'Featured Videos' which should\
        contain some Videos. These are shown at the bottom of any page. \
        Any folder with an other name that contains videos may be used as a resource \
        for a video collection. If it contains more than 3 videos it is presented as \
        a slideshow of thumbnail views. "
        
        createFolder(site, 'videoresources', 'Videoresources', description = descr)


    videoresources = site['videoresources']

    videoresources.setConstrainTypesMode(constraintypes.ENABLED)
    videoresources.setLocallyAllowedTypes(['on.video.Video', 'Folder'])
    videoresources.setImmediatelyAddableTypes(['on.video.Video', 'Folder'])

    if 'Featured Videos' not in videoresources.keys():

        descr = "Copy & paste some videos into this Folder that should be shown \
        at the bottom of any text page. If there are more than 5 Videos in here, \
        only the latest 5 are shown. If there are less than 3, The site will automatically \
        retrieve the latest videos until it has 3 of them to display. "

        createFolder(videoresources, 'featured_videos', 'Featured Videos', description = descr)
        
    featured = videoresources['featured_videos']

    featured.setConstrainTypesMode(constraintypes.ENABLED)
    featured.setLocallyAllowedTypes(['on.video.Video',])
    featured.setImmediatelyAddableTypes(['on.video.Video',])
    
        
    
