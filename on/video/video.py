# schema etc. for videos

from five import grok
from zope import schema

from plone.directives import form, dexterity

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
        title=_(u"Basename of the video file"),
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

    def __repr__(self):
        return "<ON Video at %lx>" % self

    def __str__(self):
        return "ON Video: " + self.title


import os.path
#import csv
import re
from Acquisition import aq_inner
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from on.video.configuration import IVideoConfiguration

class vVideo(object):
    """Represent one (url, formatspec) pair for a given video.
       Used to build the list of downloadable Videos.
    """
    def __init__(self, url, formatspec):
        self.url = url
        self.format = formatspec


class View(grok.View):
    grok.context(IVideo)
    grok.require('zope2.View')

    """Basic Video View"""

    def videoMetaData(self, context):
        """Read the video.metadata file to set some parameters. Helper function."""
        print "setting up video meta data for ", context
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IVideoConfiguration)
        if settings.urlbase[-1] != '/':
            context.urlbase = context.urlbase + '/'
        bpath = os.path.join(settings.fspath, context.filename, '.')
        meta_path = bpath + "metadata"
        if not os.path.exists(meta_path):
            print "no metadata for ", context
            context.thumbnailurl = None
            context.playingtime = 'unknown'
            context.urls = []
            return None # can't raise an exception here
        mdfile = open(meta_path, "rb")
        # thumbnail file:
        thumb = mdfile.next().split(':', 1)
        context.thumbnailurl = None
        if thumb[0].strip() == 'thumbnail' and len(thumb) > 1 and thumb[1].strip() != '':
            context.thumbnailurl = settings.baseurl + thumb[1].strip()

        # playing time:
        ptime = mdfile.next().split(':', 1)
        if ptime[0].strip() == 'playing time' and len(ptime) > 1:
            pt = re.search('(\d+:\d\d:\d\d)', ptime[1])
            if pt:
                context.playingtime = pt.group()
            else:
                context.playingtime = 'unknown' #None #'0:00:00' # unnown playing time

        # set url to the video that should be played inline (how to manage different sizes?):
        svid = mdfile.next().split(':', 1)
        if svid[0].strip() == 'selected':
            vf = None
            if len(svid) > 1:
                vf = svid[1].strip()
                if len(vf) > 1 and vf[0] == '/':
                    vf = vf[1:]
            if len(vf) and os.path.exists(os.path.join(settings.fspath, vf)):
                context.directplay = settings.urlbase + vf
        # now read the alternative formats list:
        urls = []
        for row in mdfile:
            k, v = row.split(':', 1)
            v = v.strip()
            print "checking filenames: ", os.path.join(settings.fsbase, v)
            if os.path.exists(os.path.join(settings.fsbase, v)):
                files.append(vVideo("".join(settings.baseurl, v), k))
        self.urls = urls

    def videofiles(self):
        """Return a list of video urls"""
        context = aq_inner(self.context)
        try:
            x = context.urls
        except:
            self.videoMetaData(context)
        #if not context.has_attr('urls'):
        #    context.videoMetaData(context)
        return context.urls

    def thumbnailurl(self):
        """Calculate the URL to the thumbnail"""
        context = aq_inner(self.context)
        try:
            x = context.urls
        except:
            self.videoMetaData(context)
        if context.thumbnailurl is not None:
            return context.thumbnailurl;
        else:
            return '/++resource++on.video/nothumbnail.png'

    def playingtime(self):
        """return the string for the playing time, if any"""
        context = aq_inner(self.context)
        try:
            x = context.urls
        except:
            self.videoMetaData()
        return context.playing_time
