
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
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

from plone.app.testing import setRoles

from on.video.testing import ON_VIDEO_FUNCTIONAL_TESTING

### swapping out this browser after reading more of the
### optilux.cinemacontent tests

# from Testing.testbrowser import Browser

from plone.testing.z2 import Browser

from zope.publisher.browser import TestRequest

class TestOnVideoHandling(unittest.TestCase):
    """Test the code for handling video objects, views etc."""

    layer = ON_VIDEO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IVideoConfiguration)
        # generate a set of mockup files:
        self.td = tempfile.mkdtemp(prefix = "on.video-tests.")
        sampledata = os.path.join(os.path.dirname(__file__), 'sample_video_1.metadata')
        shutil.copy(sampledata, self.td)
        sampledata = os.path.join(os.path.dirname(__file__), 'sample_video_2.metadata')
        shutil.copy(sampledata, self.td)
        videofiles = ('sample_video_1_big.ogv', 'sample_video_1_medium.ogv', 'sample_video_1.divx',
                      'sample_video_2.mp4', 'sample_video_2.flv')
        for video in videofiles:
            o = open(os.path.join(self.td, video), "wb")
            o.write("1")
            o.close()
        self.settings.fspath = unicode(self.td)
        #self.browser_ = Browser()
        #self.request_ = TestRequest()


    def tearDown(self):
        """remove the temp stuff"""
        shutil.rmtree(self.td)

    def test_create_video_object(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        #registry = queryUtility(IRegistry)
        #settings = registry.forInterface(IVideoConfiguration)
        v = self.portal.invokeFactory('on.video.Video', 'video1', title=u"My Sample Video")
        self.failUnless(v in self.portal)


    def test_read_video_metadata(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        #registry = queryUtility(IRegistry)
        #settings = registry.forInterface(IVideoConfiguration)
        v = self.portal.invokeFactory('on.video.Video', 'video1', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        #self.failUnless(v in self.portal)
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        #import pdb; pdb.set_trace()
        url = browser.open(video.absolute_url())
        print "url: ", url





    def test_video_format_thingy(self):
        from on.video.video import vVideo

        v = vVideo("bla.ogv", "OGV")
        self.failUnless(v.url == 'bla.ogv')
        self.failUnless(v.format == 'OGV')


    def XXtest_inspect_video(self):
        """Access the created video via the browser and see whether the metadata
           file is being parsed correctly.
        """
        from on.video import video
        # What is the correct API?
        #import pdb; pdb.set_trace()
        v = video.IVideo()
        #print "v: ", v
        self.failUnless(str(v) == 'bla')



# see http://pastie.org/3006184 for a usage problem
