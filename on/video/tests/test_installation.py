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

#from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
#from zope.component import getUtilitiesFor

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


class TestOnVideo(unittest.TestCase):
    layer = ON_VIDEO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_install_on_video(self):
        quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(quickinstaller.isProductInstalled('on.video'))

    def test_video_object(self):
        """Create a video object and inspect its attributes to see whether
           it conforms to the specs.
        """
        1 == 0
        
