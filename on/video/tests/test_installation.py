# Testing on.video in Plone 4.1, using plone.app.testing:

import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from plone.testing import z2
from plone.registry.interfaces import IRegistry

class OnVideoFixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import on.video
        self.loadZCML(package=on.video)

    def setUpPloneSite(self, portal):
        """Run the GS profile for this product"""
        self.applyProfile(portal, 'on.video:default')


    def tearDownZope(self, app):
        """Uninstall the product and destroy the Zope site"""
        z2.uninstallProduct(app, 'on.video')


ON_VIDEO_FIXTURE = OnVideoFixture()
ON_VIDEO_INTEGRATION_TESTING = IntegrationTesting(bases=(ON_VIDEO_FIXTURE,), name="OnVideoFixture:Integration")
ON_VIDEO_FUNCTIONAL_TESTING = FunctionalTesting(bases=(ON_VIDEO_FIXTURE,), name="OnVideoFixture:Functional")

from datetime import datetime

from zope.component import queryUtility
from zope.component import adapts, getMultiAdapter

from on.video.configuration import IVideoConfiguration
from on.video import config

class TestOnVideoConfig(unittest.TestCase):
    """Test the configuration of the product."""

    layer = ON_VIDEO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_video_config_registry(self):
        """Verify that the default values in the registry have been set."""
        registry = queryUtility(IRegistry)
        self.assertNotEqual(registry, None)
        settings = registry.forInterface(IVideoConfiguration)
        self.assertEqual(settings.fspath, config.ON_VIDEO_FS_PATH)
        self.assertEqual(settings.urlbase, config.ON_VIDEO_URL)

    def test_install_on_video(self):
        quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(quickinstaller.isProductInstalled('on.video'))

    def test_video_controlpanel_view(self):
        """Can we see the control panel?"""
        view = getMultiAdapter((self.portal, self.portal.REQUEST), 
                               name="on-video-settings")
        view = view.__of__(self.portal)
        configlet = view()
        self.failUnless('name="form.widgets.urlbase"' in configlet)
        self.failUnless('name="form.widgets.fspath"' in configlet)

    def test_video_control_panel_protected(self):
        """Can only we access the control panel?"""
        from AccessControl import Unauthorized
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@on-video-settings')

    def test_video_control_panel_read_url(self):
        """Retrieve the URL from the control panel"""
        registry = queryUtility(IRegistry)
        urlbase = registry.records[
            'on.video.configuration.IVideoConfiguration.urlbase']
        self.failUnless('urlbase' in IVideoConfiguration)
        self.assertEquals(urlbase.value, config.ON_VIDEO_URL)

    def test_video_control_panel_read_fs(self):
        """Retrieve the file system path from the control panel"""
        registry = queryUtility(IRegistry)
        fspath = registry.records[
            'on.video.configuration.IVideoConfiguration.fspath']
        self.failUnless('fspath' in IVideoConfiguration)
        self.assertEquals(fspath.value, config.ON_VIDEO_FS_PATH)

# now create some mock files and directories

import os
import tempfile
import shutil


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
