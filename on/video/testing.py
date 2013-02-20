# Testing on.video in Plone 4.1, using plone.app.testing:

# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

import unittest2 as unittest
#from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import Products.CMFPlone

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

#from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from plone.testing import z2
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

class OnVideoFixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import on.video
        self.loadZCML(package=on.video)

    def setUpPloneSite(self, portal):
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setDefaultChain('folder_workflow')
        """Run the GS profile for this product"""
        self.applyProfile(portal, 'on.video:default')

    def tearDownZope(self, app):
        """Uninstall the product and destroy the Zope site"""
        z2.uninstallProduct(app, 'on.video')

    def manager_browser(self):
        """Browser of Manager - not accessible from test layer
        """
        return self._auth_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    

ON_VIDEO_FIXTURE = OnVideoFixture()
ON_VIDEO_INTEGRATION_TESTING = IntegrationTesting(bases=(ON_VIDEO_FIXTURE,), name="OnVideoFixture:Integration")
ON_VIDEO_FUNCTIONAL_TESTING = FunctionalTesting(bases=(ON_VIDEO_FIXTURE,), name="OnVideoFixture:Functional")
