# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3


from datetime import datetime

from zope.component import queryUtility
from zope.component import adapts, getMultiAdapter

import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from plone.app.testing import TEST_USER_ID
#from plone.app.testing import TEST_USER_NAME
#from plone.app.testing import TEST_USER_PASSWORD

from plone.app.testing import setRoles

from on.video.testing import ON_VIDEO_INTEGRATION_TESTING

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

