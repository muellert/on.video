# Testing on.video in Plone 4.1, using plone.app.testing:

import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles

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


from zope.component import queryUtility
from on.video.configuration import IVideoConfiguration
from on.video import config

class TestOnVideo(unittest.TestCase):
    layer = ON_VIDEO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_01_install_on_video(self):
        quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(quickinstaller.isProductInstalled('on.video'))

    def XXtest_02_video_config(self):
        """try to find the config utility and play around"""
        cu = queryUtility(IVideoConfiguration, name=u"")
        self.assertNotEqual(cu, None)
        self.assertEqual(cu.fspath, config.ON_VIDEO_FS_PATH)
        self.assertEqual(cu.urlbase, config.ON_VIDEO_URL)

    def test_02_video_config_registry(self):
        """Verify that the default values in the registry have been set."""
        registry = queryUtility(IRegistry)
        self.assertNotEqual(registry, None)
        settings = registry.forInterface(IVideoConfiguration)
        self.assertEqual(settings.fspath, config.ON_VIDEO_FS_PATH)
        self.assertEqual(settings.urlbase, config.ON_VIDEO_URL)


    def test_video_object(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        
        
