from zope.component import getUtility, getMultiAdapter
from zope.site.hooks import setHooks, setSite
from zope.component import getUtility, getMultiAdapter

from zope.interface import directlyProvides

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from on.video.browser import featuredportlet
from on.video.testing import ON_VIDEO_FUNCTIONAL_TESTING
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2

from plone.app.layout.navigation.interfaces import INavigationRoot

import unittest2 as unittest

class TestPortlet(unittest.TestCase):

    layer = ON_VIDEO_FUNCTIONAL_TESTING

    def setUp(self):
        setHooks()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.browser = z2.Browser(self.portal)

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'irill.theme')

    def testPortletTypeRegistered(self):
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        # portlet = getUtility(IPortletType, name='irill.FeaturedVideos')
        # self.assertEquals(portlet.addview, 'irill.FeaturedVideos')
        import pdb; pdb.set_trace()
        self.failUnless('irill.FeaturedVideos' in manager)

    def testInterfaces(self):
        portlet = featuredportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='irill.FeaturedVideos')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], featuredportlet.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.portal.REQUEST

        mapping['foo'] = featuredportlet.Assignment(header='test portlet', entries = 5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, featuredportlet.EditForm))

    def testRenderer(self):
        context = self.portal
        request = context.REQUEST
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = featuredportlet.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, featuredportlet.Renderer))
