# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

from datetime import datetime

from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
#from zope.component import adapts, getMultiAdapter

from plone.registry.interfaces import IRegistry
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD,TEST_USER_NAME, TEST_USER_ID, TEST_USER_PASSWORD
from plone.app.testing import login

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
        # setRoles(self.portal, TEST_USER_ID, ['Manager'])
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
        # site.invokeFactory("Folder", id='testfolder', title='Testfolder')
        # testfolder = site['testfolder']
        app = self.layer['app']
        import pdb; pdb.set_trace()
        browser = self.manager_browser()
        browser.handleErrors = False
        # the following line yields a "page not found" error
        browser.open(app.plone.absolute_url() + '/videoresources')
        self.failUnless("Video Gallery" in browser.contents)

"""

(Pdb) dir(self.layer)
['__bases__', '__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__init__', '__module__', '__name__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_mergeResourceManagers', '_resourceResolutionOrder', '_resources', 'baseResolutionOrder', 'defaultBases', 'get', 'setUp', 'setUpEnvironment', 'tearDown', 'tearDownEnvironment', 'testSetUp', 'testTearDown']
(Pdb) self.layer.__dict__
{'baseResolutionOrder': (<Layer 'on.video.testing.OnVideoFixture:Functional'>, <Layer 'on.video.testing.OnVideoFixture'>, <Layer 'plone.app.testing.layers.PloneFixture'>, <Layer 'plone.testing.z2.Startup'>, <Layer 'plone.testing.zca.LayerCleanup'>), '__name__': 'OnVideoFixture:Functional', '__module__': 'on.video.testing', '__bases__': (<Layer 'on.video.testing.OnVideoFixture'>,), '_resources': {'portal': [[<PloneSite at /plone>, <Layer 'on.video.testing.OnVideoFixture:Functional'>]], 'app': [[<Application at >, <Layer 'on.video.testing.OnVideoFixture:Functional'>]], 'request': [[<HTTPRequest, URL=http://nohost>, <Layer 'on.video.testing.OnVideoFixture:Functional'>]]}}

"""
