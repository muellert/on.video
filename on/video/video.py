# schema etc. for videos

from five import grok
from zope import schema

from plone.directives import form, dexterity
from plone.memoize.instance import memoize

from plone.app.textfield import RichText

from plone.namedfile.field import NamedImage

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

    #excludeFromNav = schema.Bool(
    #    title=_('Exclude from navigation'),
    #    default=False
    #    )

    def __repr__(self):
        return "<ON Video at %lx>" % self

    def __str__(self):
        return "ON Video: " + self.title



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


# I don't have a clue about videos - suggestions for improvements
# are highly welcome!

dl_vtypes = ('video/ogg', 'video/webm', 'video/mp4', 'video/quicktime',
                 'video/x-msvideo', 'application/x-shockwave-flash',
                 'application/octet-stream')
player_vtypes = ('video/mp4', 'video/ogg', 'video/webm',
                     'video/quicktime', 'video/x-msvideo',
                     'application/x-shockwave-flash',
                     'application/octet-stream')


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
    view.thumbnailurl = '/++resource++on.video/novideo.png'
    context.playing_time = '00:00:00'
    view.videos = []
    view.playfiles = []

def fixupConfig():
    """Fix up the configuration, if required."""
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IVideoConfiguration)
    if settings.urlbase[-1] != '/':
        settings.urlbase = settings.urlbase + '/'
    if not (os.path.exists(settings.fspath) and os.path.isdir(settings.fspath)):
        print "The configured path '%s' is not a directory, setting it to /tmp" % settings.fspath
        settings.fspath = '/tmp'        # fake it...
    return settings

def getMetaDataFileHandle(view, context):
    """Find the metadata file and open it, fixing up the registry
       along the way.
    """
    #print "getMetaDataFileHandle(%s, %s)" % (str(view), str(context))
    settings = fixupConfig()
    view.player = settings.urlbase + config.PLAYER
    bpath = os.path.join(settings.fspath, context.filename)
    meta_path = bpath + ".metadata"
    view.thumbnailurl = None
    if not os.path.exists(meta_path):
        print "no metadata for ", context
        setDefaultNoVideoValues(view, context)
        return None, settings
    mdfile = open(meta_path, "rb")
    # thumbnail file:
    thumb = mdfile.next().split(':', 1)
    if thumb[0].strip() == 'thumbnail' and len(thumb) > 1 and thumb[1].strip() != '':
        view.thumbnailurl = settings.urlbase + thumb[1].strip()
    return mdfile, settings


class View(grok.View):
    grok.context(IVideo)
    grok.require('zope2.View')

    """Basic Video View"""

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.readVideoMetaData(context)

    def readVideoMetaData(self, context):
        """Read the video.metadata file to set some parameters. Helper function.
        """
        (mdfile, settings) = getMetaDataFileHandle(self, context)
        if not mdfile:                  # integrity error, but hey...
            return

        # playing time:
        ptime = mdfile.next().split(':', 1)
        if ptime[0].strip() == 'playing time' and len(ptime) > 1:
            pt = re.search('(\d+:\d\d:\d\d)', ptime[1])
            if pt:
                context.playing_time = pt.group()
            else:
                context.playing_time = 'unknown' #None #'0:00:00' # unnown playing time

        # set url to the video that should be played inline (how to manage different sizes?):
        svid = mdfile.next().split(':', 1)

        # Algorithm:
        # We need to select an MP4 format video for direct play, if possible.
        # To arrive at a consistent list of video files to play/download, we
        # only remember the file name of the selected video and see, whether
        # it occurs again later down the road (eg. should there be multiple
        # MP4 videos available).
        self.directplay = None
        directplay = None
        #import pdb; pdb.set_trace()
        if svid[0].strip() == 'selected':
            vf = None
            if len(svid) > 1:
                vf = svid[1].strip()
                if len(vf) > 1 and vf[0] == '/':
                    vf = vf[1:]
            if len(vf) and os.path.exists(os.path.join(settings.fspath, vf)):
                directplay = vf
        # now read the alternative formats list:
        # make the videos unique:
        videos = {}
        #print "--- readVideoMetaData(): videos = ", videos
        for row in mdfile:
            #print "... readVideoMetaData(): current row: -->%s<--" % row
            if ':' not in row:
                break
            # k: format, v: filename
            k, v = row.split(':', 1)
            v = v.strip()
            #print "checking filenames: ", os.path.join(settings.fspath, v)
            if not k in videos.keys() and os.path.exists(os.path.join(settings.fspath, v)):
                videos[k] = vVideo(settings.urlbase + v, k)
                #print "--- readVideoMetaData(): videos[%s] = %s" % (str(k), str(videos[k]))
        mdfile.close()
        vlist = videos.values()
        #print "videos: ", vlist
        self.playfiles = sortVideosForPlayer(vlist, directplay)
        #print "*** readVideoMetaData(): videos for player: ", [ r.url for r in self.playfiles ]
        #print "*** readVideoMetaData(): videos for player, types: ", [ r.filetype for r in self.playfiles ]
        self.directplay = self.playfiles[0]
        # deep copy!!!
        downloadlist = self.playfiles[:]
        self.videos = sortVideosForDownload(downloadlist)

    @memoize
    def videofiles(self):
        """Return a list of video urls for download"""
        context = aq_inner(self.context)
        return self.videos

    @memoize
    def playerchoices(self):
        """Return a list of video urls for the player"""
        context = aq_inner(self.context)
        #print "=== View.playerchoices(): videos for player: ", [ r.url for r in self.playfiles ]
        #print "=== View.playerchoices(): videos for player, types: ", [ r.filetype for r in self.playfiles ]
        return self.playfiles

    @memoize
    def playingtime(self):
        """return the string for the playing time, if any"""
        context = aq_inner(self.context)
        return context.playing_time

    @memoize
    def thumbnail(self):
        """Calculate the URL to the thumbnail"""
        context = aq_inner(self.context)
        if self.thumbnailurl is not None:
            return self.thumbnailurl;
        else:
            return '/++resource++on.video/nothumbnail.png'

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
