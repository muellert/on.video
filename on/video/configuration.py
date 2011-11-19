# schema etc. for videos

from five import grok
from zope import schema

from plone.directives import form, dexterity

from on.video import _


class IVideoConfiguration(form.Schema):
    """Configuration for the whole package.
    """

    fspath = schema.Text(
        title=_(u"File system path to the storage of the videos"),
        )

    urlbase = schema.Text(
        title=_(u"Base URL for generated links. The full link will look like urlbase + filename + filetype."),
        )
