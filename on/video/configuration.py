# schema etc. for videos

# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3


import os, os.path

from five import grok
from zope import schema
from zope.interface import implements
from plone.directives import form, dexterity

from on.video import _

from on.video import config


class IVideoConfiguration(form.Schema):
    """Configuration for the whole package.
    """

    fspath = schema.TextLine(
        title=_(u"File System Path"),
        description=_(u"File system path to the directory where the video files are stored."),
        required = True,
        default = config.ON_VIDEO_FS_PATH,
        )

    urlbase = schema.URI(
        title=_(u"Base URL"),
        description=_(u"Base URL for generated links. The full URL will "
                      "look like urlbase + filename + filetype."),
        required = True,
        default = config.ON_VIDEO_URL,
        )

from plone.app.registry.browser import controlpanel

class VideoConfigurationEditForm(controlpanel.RegistryEditForm):

    schema = IVideoConfiguration
    label = _(u"Video Product settings")
    description = _(u"""""")

    def updateFields(self):
        super(VideoConfigurationEditForm, self).updateFields()


    def updateWidgets(self):
        super(VideoConfigurationEditForm, self).updateWidgets()

class VideoConfigurationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = VideoConfigurationEditForm
