# schema etc. for videos

# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3


import logging
from five import grok
from zope import schema
from zope.interface import Interface
from urlparse import urljoin

from plone.directives import form
from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize
from plone.app.textfield import RichText

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.app.layout.viewlets.interfaces import IBelowContentBody

from Products.Archetypes.interfaces.base import IBaseContent


from on.video import _


class IVideo(form.Schema):
    """A video metadata object.
    """

    title = schema.TextLine(
        title=_(u"Name"),
        )
    
    director = schema.TextLine(
        title=_(u"Author/Director"),
        )

    recorded = schema.Datetime(
        title=_(u"Date of recording"),
        #required=False,
        )
    
    place = schema.Text(
        title=_(u"Location of recording"),
        )

    filename = schema.TextLine(
        title=_(u"Basename of the video file - eg. for 'myvideo.ogv', enter 'myvideo'."),
        )

    description = schema.Text(
        title=_(u"Teaser"),
        description=_(u"Please put in a short summary about the "
                      "video in here. No formatting allowed."),
        required=False
        )
    
    body = RichText(
        title=_(u"Long description (allows some HTML)"),
        )



import os.path
import re
from Acquisition import aq_inner
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from on.video.configuration import IVideoConfiguration

filetypes = {'mp4': 'video/mp4',
             'mpeg': 'video/mpeg',
             'flv': 'application/x-shockwave-flash',
             'ogv': 'video/ogg',
             'webm': 'video/webm',
             'avi': 'video/x-msvideo',
             'mov': 'video/quicktime',
             }


class vVideo(object):
    """Represent one (url, formatspec) pair for a given video.
       Used to build the list of downloadable Videos.
    """
    def __init__(self, url, formatspec):
        self.url = url
        self.displayformat = formatspec
        self.filetype = self.calculateFileType(url)

    @classmethod
    def calculateFileType(cls, name):
        """Do the windows thing and 'determine' the file type from the extension."""
        name = name.lower()
        slashpos = name.rfind('/')
        if slashpos >= 0:
            lastpart = name[slashpos + 1:]
        else:
            lastpart = name
        dotpos = lastpart.rfind('.')
        if dotpos >= 0:
            extension = lastpart[dotpos + 1:]
        else:
            extension = ''
        if extension in filetypes.keys():
            ftype = filetypes[extension]
        else:
            ftype = 'application/octet-stream'
        return ftype


dl_vtypes = ('video/ogg', 'video/webm', 'video/mp4', 'video/quicktime',
                 'video/x-msvideo', 'application/x-shockwave-flash',
                 'application/octet-stream')
player_vtypes = ('video/mp4', 'video/ogg', 'video/webm',
                     'video/quicktime', 'video/x-msvideo',
                     'application/x-shockwave-flash',
                     'application/octet-stream')


def genUrl(prefix, folderspec, filename):
    """Concatenate these three elements and make them a real URL.
       No luck with urljoin(), so do it by hand for now.
    """
    tail = filename
    if folderspec:
        tail = folderspec + '/' + filename
    return prefix + tail
        

def sortVideosList(videos, desiredsorting):
    """Sort the videos according to the list of extensions in
       'desiredsorting'. No special sorting algorithm used,
       due to the estimated small size of the list.
    """
    result = []
    #print ">>> sortVideosList: videos = ", [ v.url for v in videos ]
    for ext in desiredsorting:
        #print "=== sortVideosList: videos = ", [ v.url for v in videos ]
        video = 0
        while len(videos) > 0 and video < len(videos):
            #print "--- checking video: ", video
            if videos[video].filetype == ext:
                result.append(videos[video])
                videos.pop(video)
                #print "--- appended ", result[-1].url
            else:
                video += 1
    #print "<<< sortVideosList: result = ", [ v.url for v in result ]
    return result

def sortVideosForDownload(videos):
    """Sort the videos for download, according to freeness and
       features. The 'videos' parameter is a list of vVideo
       objects.
    """
    return sortVideosList(videos, dl_vtypes)

def sortVideosForPlayer(videos, selected):
    """Sort the videos for download, according to freeness and
       features. The 'videos' parameter is a list of vVideo
       objects. Try to get the selected video into the first
       position, but only if it is an MP4.
    """
    #print ">>> sortVideosForPlayer(%s, %s)" % (str([ v.url for v in videos]), selected)
    result = sortVideosList(videos, player_vtypes)
    #print "--- sortVideosForPlayer(): result = ", [ v.url for v in result]
    if selected and (selected.endswith('mp4') or selected.endswith('MP4')):
        pos = 0
        for video in result:
            if video.url.endswith(selected):
                break
            pos += 1
        if pos > 0:
            swap = result[pos]
            result[pos] = result[0]
            result[0] = swap
    return result


import config


def setDefaultNoVideoValues(view, context):
    from config import DEFAULT_WIDTH
    from config import DEFAULT_HEIGHT
    view.thumbnailurl = '/++resource++on.video/novideo.png'
    view.playing_time = 'unknown' # '00:00:00'
    view.videos = []
    view.playfiles = []
    # special case: metafile is present, but not the actual video
    if not hasattr(view, "y") or not isinstance(view.x, int):
	view.x = DEFAULT_WIDTH
    if not hasattr(view, "y") or not isinstance(view.y, int):
	view.y = DEFAULT_HEIGHT


def fixupConfig():
    """Fix up the configuration, if required."""
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IVideoConfiguration)
    if settings.urlbase[-1] != '/':
        settings.urlbase = settings.urlbase + '/'
    if not (os.path.exists(settings.fspath) and os.path.isdir(settings.fspath)):
        logger = logging.getLogger('on.video')
        logging.warn("The configured path '%s' is not a directory, setting it to /tmp" % settings.fspath)
        settings.fspath = u'/tmp'        # fake it...
    return settings

def getMetaDataFileHandle(view, context):
    """Find the metadata file and open it, fixing up the registry
       along the way.
    """
    # print "getMetaDataFileHandle(%s, %s)" % (str(view), str(context))
    settings = fixupConfig()
    view.player = settings.urlbase + config.PLAYER
    bpath = os.path.join(settings.fspath, context.filename)
    meta_path = bpath + ".metadata"
    # print "getMetaDataFileHandle() meta_path = %s" % meta_path
    # print "metadata: ", meta_path
    view.urlprefix = ""
    if '/' in context.filename:
        view.urlprefix = context.filename[:context.filename.rfind('/')]
    #print "urlprefix: ", view.urlprefix
    #import pdb; pdb.set_trace()
    if not os.path.exists(meta_path):
        #print "no metadata for ", context
        setDefaultNoVideoValues(view, context)
        view.thumbnailurl = '/++resource++on.video/nometafile.png'
        return None, settings
    mdfile = open(meta_path, "rb")
    # thumbnail file:
    view.thumbnailurl = None
    lines = mdfile.readlines(2000)
    mdfile.close()
    line = lines.pop(0)
    thumb = line.split(':', 1)
    if thumb[0].strip() == 'thumbnail' and len(thumb) > 1 and thumb[1].strip() != '':
        view.thumbnailurl = genUrl(settings.urlbase, view.urlprefix, thumb[1].strip())
    line = lines.pop(0)
    ptime = line.split(':', 1)
    if ptime[0].strip() == 'playing time' and len(ptime) > 1:
        pt = re.search('(\d+:\d\d:\d\d)', ptime[1])
        if pt:
            view.playing_time = pt.group()
        else:
            view.playing_time = 'unknown' #None #'0:00:00' # unnown playing time
    return lines, settings


def readVideoMetaData(view, context):
    """Read the video.metadata file to set some parameters. Helper function.
    """
    from config import MAX_WIDTH
    from config import DEFAULT_WIDTH
    from config import MIN_HEIGHT
    from config import MAX_HEIGHT
    from config import DEFAULT_HEIGHT
    
    (lines, settings) = getMetaDataFileHandle(view, context)
    if not lines:                  # integrity error, but hey...
        return

    # playing time:

    # set url to the video that should be played inline (how to manage different sizes?):
    line = lines.pop(0)
    svid = line.split(':', 1)

    view._title = context.title
    # Algorithm:
    # We need to select an MP4 format video for direct play, if possible.
    # To arrive at a consistent list of video files to play/download, we
    # only remember the file name of the selected video and see, whether
    # it occurs again later down the road (eg. should there be multiple
    # MP4 videos available).
    view.directplay = None
    directplay = None
    #print "*** readVideoMetaData(), urlprefix = ", view.urlprefix
    if svid[0].strip() == 'selected':
        vf = None
        if len(svid) > 1:
            vf = svid[1].strip()
            if len(vf) > 1 and vf[0] == '/':
                vf = vf[1:]
        if len(vf) and os.path.exists(os.path.join(settings.fspath, view.urlprefix, vf)):
            directplay = vf

    view.x = DEFAULT_WIDTH
    view.y = DEFAULT_HEIGHT
    if 'default size' in lines[0]:          # skip if we don't have it, but don't eat the line
        line = lines.pop(0)
        dimensions = line.split(':', 1)
        #print "*** reading the specified default size: ", dimensions
        x, y = map(int, dimensions[1].strip().split('x', 1))
        #print "\t\tx = %d, y = %d" % (x, y)
        # make sure the video doesn't get too small or too big:
        if x < 100 or x > MAX_WIDTH:
            #print "need to adjust the default size (x)"
            x = DEFAULT_WIDTH
        if y < MIN_HEIGHT or y > MAX_HEIGHT:
            #print "need to adjust the default size (y)"
            y = x * DEFAULT_HEIGHT/DEFAULT_WIDTH
        #print "\tafter sanitizing values: x = %d, y = %d" % (x, y)
        view.x = x
        view.y = y
    videos = {}

    for row in lines:
        #print "... readVideoMetaData(): current row: -->%s<--" % row
        if ':' not in row:
            break
        # k: format, v: filename
        k, v = row.split(':', 1)
        v = v.strip()
        #print "checking filenames: ", os.path.join(settings.fspath, view.urlprefix, v)
        if not k in videos.keys() and os.path.exists(os.path.join(settings.fspath, view.urlprefix, v)):
            v_url = genUrl(settings.urlbase, view.urlprefix, v)
            videos[k] = vVideo(v_url, k)
            #print "--- readVideoMetaData(): videos[%s] = %s" % (str(k), str(videos[k]))
    vlist = videos.values()
    #print "\tvideo dimensions before handling files: x = %d, y = %d" % (view.x, view.y)
    view.playfiles = sortVideosForPlayer(vlist, directplay)
    #print "*** readVideoMetaData(): videos for player, types: ", [ r.filetype for r in view.playfiles ]
    #view.directplay = view.playfiles[0]
    if len(view.playfiles) == 0:
        setDefaultNoVideoValues(view, context)
    # deep copy!!!
    downloadlist = view.playfiles[:]
    view.videos = sortVideosForDownload(downloadlist)
    #print "*** readVideoMetaData() done, video dimensions: x = %d, y = %d" % (view.x, view.y)


class ViewThumbnail(grok.View):
    grok.context(IVideo)
    grok.require('zope2.View')
    grok.name('summary')

    """View to display the video within an album view."""

    def __init__(self, context, request):
        super(ViewThumbnail, self).__init__(context, request)
        self.id = context.id
        readVideoMetaData(self, context)

    @memoize
    def thumbnail(self):
        """Calculate the URL to the thumbnail"""
        if self.thumbnailurl is not None:
            return self.thumbnailurl;
        else:
            return '/++resource++on.video/nothumbnail.png'

    @memoize
    def title(self):
        """Return a part of the title, suitable for a gallery view."""
        return self.context.title[:20]


class View(grok.View):
    grok.context(IVideo)
    grok.require('zope2.View')
    grok.name('view')

    """Basic Video View"""

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        readVideoMetaData(self, context)

    @memoize
    def videofiles(self):
        """Return a list of video urls for download"""
        return self.videos

    @memoize
    def playerchoices(self):
        """Return a list of video urls for the player"""
        #print "=== View.playerchoices(): videos for player, types: ", [ r.filetype for r in self.playfiles ]
        return self.playfiles

    @memoize
    def thumbnail(self):
        """Calculate the URL to the thumbnail"""
        if self.thumbnailurl is not None:
            return self.thumbnailurl;
        else:
            return '/++resource++on.video/nothumbnail.png'

    @memoize
    def x(self):
        return self.x

    @memoize
    def y(self):
        return self.y

    @memoize
    def genFlashVars(self):
        """Generate a correct config string for the flash player.

           Sample:  value="config={'playlist':['/videosGHM/Joakim_Verona-Emacs_XWidget-2-1.jpg'
                      ,{'url':'/videosGHM/Joakim_Verona-Emacs_XWidget.mp4','autoPlay':false}]}"

           (all in one line, without spaces)
        """
        thumbnail = self.thumbnail()
        try:
            video = self.directplay.url
        except:
            video = "video not available"
        config="config={'playlist':['%s',{'url':'%s','autoPlay':false}]}" % \
                (thumbnail, video)
        return config



