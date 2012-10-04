# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

from datetime import datetime

#from zope.testbrowser.browser import Browser
from plone.testing.z2 import Browser
#from zope.publisher.browser import TestRequest

from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName

import transaction

from plone.registry.interfaces import IRegistry
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import login

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



class TestVideoGallery(unittest.TestCase):
    """Test the code for handling video objects, views etc."""

    layer = ON_VIDEO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory("Folder", id='testfolder', title='Testfolder')
        transaction.commit()
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
        # delete our private content, too
        shutil.rmtree(self.td)


    def test_view_registration(self):
        """Test the availability of the gallery view."""
        app = self.layer['app']
        browser = Browser(app)
        portal = self.layer['portal']
        portalURL = portal.absolute_url()
        browser.handleErrors = False
        browser.open(portalURL + '/login_form')
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        self.failUnless("Log out" in browser.contents)
        browser.open(portalURL + '/testfolder')
        self.failUnless("Video Gallery" in browser.contents)


    def test_gallery_item_filter(self):
        """Test that only videos and folders are being included in the
           listing.
        """
        folder = self.layer['portal']['testfolder']
        for i in range(1,5):
            folder.invokeFactory('on.video.Video', id='test%d' % i)
        folder.invokeFactory('Document', id='some_document')
        folder.setLayout('on-video-gallery')
        app = self.layer['app']
        portal = self.layer['portal']
        portalURL = portal.absolute_url()
        browser = Browser(app)
        browser.addHeader('Authorization', 'Basic %s:%s' % (
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ))
        browser.open(portalURL + '/testfolder')
        self.failIf('some_document' in browser.contents)
