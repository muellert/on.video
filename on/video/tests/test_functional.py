# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

from datetime import datetime

from zope.component import queryUtility

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
from plone.testing.z2 import Browser

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
        shutil.rmtree(self.td)

    def test_create_video_object(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video1', title=u"My Sample Video")
        self.failUnless(v in self.portal)


    def test_read_video1_metadata(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video1', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_1',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        view = video.restrictedTraverse('@@view')
        downloads = view.videofiles()
        playlist = view.playerchoices()
        self.failUnless(playlist[0].url.endswith(".mp4"))
        self.failUnless(downloads[0].url.endswith(".ogv"))
        browser.open(video.absolute_url())
        self.failUnless('nothumbnail' in browser.contents)

    def test_read_video2_metadata(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video2', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_2',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        self.failUnless('nothumbnail' in browser.contents)

    def test_read_video_no_metadata(self):
        """Create a video object that has no metadata file.
           See whether the code detects this properly and
           displays the appropriate placeholder image.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video3', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'no-metadata',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        self.failUnless('nometafile' in browser.contents)

    def test_read_video_metadata_no_video(self):
        """Create a video object that has a metadata file that points to
           non-existent video files..
           See whether the code detects this properly and
           displays the appropriate placeholder image.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video5', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_4',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        self.failUnless('novideo' in browser.contents)

    def test_read_video_with_thumbnail(self):
        """Create a video object with a thumbnail.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video4', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_3',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        downloads = view.videofiles()
        playlist = view.playerchoices()
        self.failUnless(view.playing_time == '20:30:50')
        self.failUnless(playlist[0].url.endswith(".mp4"))
        self.failUnless(downloads[0].url.endswith(".ogv"))

    def test_video_summary_view(self):
        """check whether the 'summary' view for the gallery works
        """
        v = self.portal.invokeFactory('on.video.Video', 'video4', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_3',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        video = self.portal[v]
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url() + '/@@summary')
        self.failUnless('<div class="on-video-small-thumbnail">' in browser.contents)
        self.failIf('<object>' in browser.contents)

    def test_read_video_from_subdir(self):
        """See whether we can serve a video from a subdirectory.
           The hardcoded valeu for the URL prefix should be replaced
           by reading the registry.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video5', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'subfolder/sample_video_3',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        self.failUnless('http://localhost/subfolder/' in view.thumbnail())
        downloads = view.videofiles()
        for video in downloads:
            self.failUnless('http://localhost/subfolder/' in video.url)

    def test_read_video_default_dimensions_handling(self):
        """See whether the dimensions are set correctly if the metadata file
           does not include the "default size" entry.
        """
        from on.video.config import DEFAULT_WIDTH, DEFAULT_HEIGHT
        v = self.portal.invokeFactory('on.video.Video', 'video6', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_3',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        self.failUnless(view.x == DEFAULT_WIDTH)
        self.failUnless(view.y == DEFAULT_HEIGHT)

    def test_read_video_custom_dimensions_handling(self):
        """See whether the dimensions are set correctly if the metadata
	   file does include the "default size" entry.
        """
        from on.video.config import DEFAULT_WIDTH, DEFAULT_HEIGHT
        v = self.portal.invokeFactory('on.video.Video', 'video7', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_4',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        self.failUnless(view.x == 690)
        self.failUnless(view.y == 535)

    def test_read_video_weird_dimensions_handling(self):
        """See whether the dimensions are set correctly if the metadata
	   file does include the "default size" entry, but values are
	   out of bound.
        """
        from on.video.config import DEFAULT_WIDTH, DEFAULT_HEIGHT
        v = self.portal.invokeFactory('on.video.Video', 'video8', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_5',
                                      place = 'nirvana',
                                      body = '<strong>some interesting story</strong>')
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        self.failUnless(view.x == DEFAULT_WIDTH)
        self.failUnless(view.y == DEFAULT_HEIGHT)

    def test_video_format_thingy(self):
        from on.video.video import vVideo
        v = vVideo("bla.ogv", "OGV")
        self.failUnless(v.url == 'bla.ogv')
        self.failUnless(v.displayformat == 'OGV')
        self.failUnless(v.filetype == 'video/ogg')

