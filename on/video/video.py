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
    
    author = schema.TextLine(
        title=_(u"Author"),
        )

    created = schema.Datetime(
        title=_(u"Date of recording"),
        #required=False,
        )
    
    location = schema.Text(
        title=_(u"Location of recording"),
        )

    filename = schema.Text(
        title=_(u"Basename of the video file"),
        )
    
    thumbnail = NamedImage(
        title=_(u"Thumbnail"),
        description=_(u"Please upload an image"),
        required=False,
        )

    teaser = schema.Text(
        title=_(u"A short summary"),
        required=False
        )
    
    description = RichText(
        title=_(u"Long description (allows some HTML)"),
        )

