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
    
    thumbnail = NamedImage(
        title=_(u"Thumbnail"),
        description=_(u"Here you can upload an image to display as a thumbnail."),
        required=False,
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
from Acquisition import aq_inner
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from on.video.configuration import IVideoConfiguration

class vVideo(object):

    def __init__(self, url, type):
        self.url = url
        self.type = type


class View(grok.View):
    grok.context(IVideo)
    grok.require('zope2.View')

    """Basic Video View"""

    extensions = ('mp4', 'ogv', 'mpeg', 'avi', 'flv')

    def videofiles(self):
        """Return a list of video files"""
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IVideoConfiguration)
        context = aq_inner(self.context)
        bpath = settings.fspath + '/' + context.filename + '.'
        burl = settings.urlbase
        
        files = []
        # need to do something to handle sizes, too:
        for e in self.extensions:
            fn = bpath + e
            if os.path.exists(fn):
                rfn = burl + context.filename + '.' + e
                print "rfn: ", rfn
                files.append(vVideo(rfn, e))
        return files


    def thumbnailurl(self):
        """Calculate the URL to the thumbnail"""
        #if self.has_attr('thumbnail'):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IVideoConfiguration)
        context = aq_inner(self.context)
        for extension in ('png', 'jpeg', 'jpg', 'gif'):
            maybe_thumbnail = settings.fspath + '/' + context.filename + '.' + extension
            if os.path.exists(maybe_thumbnail):
                return settings.urlbase + context.filename + '.' + extension
        return '/++resource++on.video/nothumbnail.png'
        #return settings.urlbase + '++resource++on.video/nothumbnail.png'
