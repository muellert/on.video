# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

from datetime import datetime

from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from plone.app.textfield.value import RichTextValue

from on.video.testing import ON_VIDEO_FUNCTIONAL_TESTING

from on.video.configuration import IVideoConfiguration
from on.video import config
import os
import tempfile
import shutil

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

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
        videofiles = ['sample_video_1_big.ogv', 'sample_video_1_medium.ogv', 'sample_video_1.mp4',
                      'sample_video_2.mp4', 'sample_video_2.avi',
                      'sample_video_3.mp4', 'sample_video_3_medium.ogv',
                      ]
        files_to_copy = [ 'sample_video_%d.metadata' % i for i in range(1, 8) ]
        otherfiles = [ 'Vincent_Untz.metadata', 'corrupted1.metadata', 'corrupted2.metadata', 'thumb.png' ]
        files_to_copy = files_to_copy + otherfiles  + videofiles
        for f in files_to_copy:
            sampledata = os.path.join(os.path.dirname(__file__), f)
            shutil.copy(sampledata, self.td)
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
        #import pdb; pdb.set_trace()
        v = self.portal.invokeFactory('on.video.Video', 'video1', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_1',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        self.failUnless('nothumbnail' in browser.contents)

    def test_read_video3_metadata(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video2', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'Vincent_Untz',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        #print "browser.contents: ", browser.contents
        self.failUnless('novideo' in browser.contents)

    def test_read_video_with_no_playing_time(self):
        """Check the generated playlist: What about unknown file extensions?
        """
        from on.video.config import DEFAULT_WIDTH, DEFAULT_HEIGHT
        v = self.portal.invokeFactory('on.video.Video', 'video8', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_6',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        import pdb; pdb.set_trace()
        self.failUnless(view.playing_time == 'unknown')

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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        self.failUnless('nometafile' in browser.contents)

    def XXtest_add_video_via_browser_no_metadata(self):
        """Simulate adding a video object that has no metadata file.
           The validator should raise an exception, which should
           yield an error message in the browser.

           We first need to learn about properly writing browser tests.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video',
                                      title=u"My Sample Unavailable Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'no-metadata',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url())
        #print "browser.contents: ", browser.contents
        self.failUnless('novideo' in browser.contents)
        ### Disabled, because we so far inherently ignore unknown files:
        #self.failUnless('application/octet-stream' in browser.contents)

    def test_read_video_with_thumbnail(self):
        """Create a video object with a thumbnail.
        """
        v = self.portal.invokeFactory('on.video.Video', 'video4', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_3',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        video = self.portal[v]
        import transaction; transaction.commit()
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        video = self.portal[v]
        browser.open(video.absolute_url() + '/@@summary')
        self.failUnless('<div class="on-video-small-thumbnail">' in browser.contents)
        self.failIf('<object>' in browser.contents)

    def test_video_summary_view(self):
        """check whether the 'summary' view for the gallery works
        """
        v = self.portal.invokeFactory('on.video.Video', 'video4', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_3',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
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
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        self.failUnless(view.x == DEFAULT_WIDTH)
        self.failUnless(view.y == DEFAULT_HEIGHT)

    def test_read_video_with_no_playing_time(self):
        """See whether the file is correctly read if the playing time
           is not specified.
        """
        from on.video.config import DEFAULT_WIDTH, DEFAULT_HEIGHT
        v = self.portal.invokeFactory('on.video.Video', 'video8', title=u"My Sample Video",
                                      name = 'some kind of video',
                                      author = 'me, myself',
                                      recorded = datetime.now(),
                                      filename = 'sample_video_6',
                                      place = 'nirvana',
                                      body = RichTextValue('<strong>some interesting story</strong>'))
        video = self.portal[v]
        import transaction; transaction.commit()
        view = video.restrictedTraverse('@@view')
        self.failUnless(view.playing_time == 'unknown')

    def test_fix_settings_url(self):
        """See whether the URL is properly fixed.
        """
        from on.video.video import fixupConfig
        oldsettings = self.settings
        self.settings.urlbase = 'http://nohost'
        fixupConfig()
        self.failUnless(self.settings.urlbase.endswith('/'))

    def test_fix_settings_fspath(self):
        """See whether the file system path is properly reset.
        """
        from on.video.video import fixupConfig
        oldsettings = self.settings
        self.settings.fspath = u'/nosuchfileordirectory'
        fixupConfig()
        self.failUnless(self.settings.fspath == u'/tmp')

    def test_video_format_thingy(self):
        from on.video.video import vVideo
        v = vVideo("bla.ogv", "OGV")
        self.failUnless(v.url == 'bla.ogv')
        self.failUnless(v.displayformat == 'OGV')
        self.failUnless(v.filetype == 'video/ogg')

    def test_rejection_of_corrupted_files(self):
        from on.video.video import parseMetadataFileContents, fixupConfig, getMetaDataFileLines
        settings = fixupConfig()
        lines = getMetaDataFileLines(settings.fspath, 'corrupted1')
        vo = parseMetadataFileContents(lines, settings.urlbase, settings.fspath, 'corrupted1')
        self.failUnless(vo.thumbnailurl == '/++resource++on.video/invalidmetafile.png')


    def test_add_video_without_title(self):
        """Fill out the video 'add' form with the wrong date and notice
           that it does not validate.
        """
        app = self.layer['app']
        browser = Browser(app)
        #browser.handleErrors = False
        # get the relevant fields:
        browser.addHeader('Authorization', 'Basic %s:%s' % (
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        browser.open(self.portal.absolute_url() + '/++add++on.video.Video')
        title_field = browser.getControl(name='form.widgets.title')
        recorded_field_year = browser.getControl(name='form.widgets.recorded-year')
        recorded_field_month = browser.getControl(name='form.widgets.recorded-month')
        recorded_field_day = browser.getControl(name='form.widgets.recorded-day')
        recorded_field_hour = browser.getControl(name='form.widgets.recorded-hour')
        recorded_field_min = browser.getControl(name='form.widgets.recorded-min')
        filename_field = browser.getControl(name='form.widgets.filename')
        body_field = browser.getControl(name='form.widgets.body')
        save_button = browser.getControl(name='form.buttons.save')
        # fill the fields and save the form:
        filename_field.value = u'sample_video_3'
        body_field.value = u'<p>nothing to see here, move along</p>'
        save_button.click()
        #import pdb; pdb.set_trace()
        vl = self.portal.keys()
        #self.failUnless(True)
