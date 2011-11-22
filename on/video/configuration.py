# schema etc. for videos

import os, os.path

from five import grok
from zope.interface import implements
from plone.directives import form, dexterity

from on.video import _

import config

class VideoConfiguration(object):
    """Store the file system path to the videos and the base URL to be
       generated to download them in class attributes.
    """

    implements(IVideoConfiguration)

    fspath = config.ON_VIDEO_FS_PATH
    urlbase = config.ON_VIDEO_URL

    def __call__(self, fspath_ = None, urlbase_ = None):
        """Modify the class attributes, but leave out consistency
           checks, like 'is the url valid' for later.
        """
        if fspath_:
            self.__class__.fspath = fspath_
        if urlbase_:
            self.__class__.urlbase = urlbase_

