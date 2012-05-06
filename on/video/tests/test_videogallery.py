# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

from datetime import datetime

from zope.component import queryUtility
#from zope.component import adapts, getMultiAdapter

from plone.registry.interfaces import IRegistry

from on.video.testing import ON_VIDEO_FUNCTIONAL_TESTING

from on.video.configuration import IVideoConfiguration
from on.video import config
import os
import tempfile
import shutil

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
#from plone.app.testing import TEST_USER_NAME
#from plone.app.testing import TEST_USER_PASSWORD

from plone.app.testing import setRoles

from on.video.testing import ON_VIDEO_FUNCTIONAL_TESTING
from on.video.setuphandlers import createFolder

from plone.testing.z2 import Browser

#from zope.publisher.browser import TestRequest

class TestVideoGallery(unittest.TestCase):
    """Test the code for handling video objects, views etc."""

    layer = ON_VIDEO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IVideoConfiguration)
        # generate a set of mockup files:
        self.td = tempfile.mkdtemp(prefix = "on.video-tests.")
        for i in range(1, 6):
            sampledata = os.path.join(os.path.dirname(__file__), 'sample_video_%d.metadata' % i)
            shutil.copy(sampledata, self.td)
        sampledata = os.path.join(os.path.dirname(__file__), 'thumb.png')
        shutil.copy(sampledata, self.td)
        videofiles = ('sample_video_1_big.ogv', 'sample_video_1_medium.ogv', 'sample_video_1.mp4',
                      'sample_video_2.mp4', 'sample_video_2.avi',
                      'sample_video_3.mp4', 'sample_video_3_medium.ogv',
                      )
        subdir = os.path.join(self.td, "subfolder")
        os.mkdir(subdir)
        sampledata = os.path.join(os.path.dirname(__file__), 'sample_video_3.metadata')
        shutil.copy(sampledata, subdir)
        for d in self.td, subdir:
            for video in videofiles:
                o = open(os.path.join(d, video), "wb")
                o.write("1")
                o.close()

        self.settings.fspath = unicode(self.td)


    def tearDown(self):
        """remove the temp stuff"""
        #print "Please remove the test dir, ", self.td
        shutil.rmtree(self.td)

    def test_view_registration(self):
        site = self.portal
        site.invokeFactory("Folder", id='testfolder', title='Testfolder')
        testfolder = site['testfolder']
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        import pdb; pdb.set_trace()
        # the following line yields a "page not found" error
        browser.open(testfolder.absolute_url())
        self.failUnless("Video Gallery" in browser.contents)

