### copyright (c) 2012-2013 Toni Mueller <support@oeko.net>
### AGPLv3 if possible, otherwise GPLv3 or later
### incorporates portions of code from ore.contentmirror

"""
Usage:

./bin/instance run addvideos PORTAL_PATH FS_PATH


PORTAL_PATH: root folder for a Plone site in the ZODB (eg. /01/mnt/Plone)

FS_PATH: path where existing video files (.metadata) reside

The configured root path for all videos should be a prefix of FS_PATH,
otherwise your results will be garbage.

The target Plone site must have the on.video product installed,
otherwise this script will not work.

"""

import os
import os.path
import re
import sys
import optparse


try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from datetime import datetime

import transaction

from Products.Five import zcml
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.app.component.hooks import setSite
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.locales import locales
from zope.interface import implements
from zope.app.component.hooks import getSite
from Products.CMFCore.exceptions import BadRequest
from plone.uuid.interfaces import IMutableUUID
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.utils import dt2DT

from Products.CMFCore.utils import getToolByName

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
#from AccessControl.Owner import changeOwnership
from Products.CMFCore import permissions
from plone.app.textfield.value import RichTextValue

from plone.registry.interfaces import IRegistry
from on.video.configuration import IVideoConfiguration

#from zopestuff import recreateSite

#from config import dburl, targetpath


site = None                             # the site we are working on

catalog = None

stdlicense = """
<a class="video-copyright-link" title="CC-BY-NC-ND" href="http://creativecommons.org/licenses/by-nc-nd/3.0/fr/">
<img title="Creative Commons BY-NC-ND" sclass="video-copyright-image" rc="resolveuid/525e886f48314790b6b83b3446ab4fb5" alt="Creative Commons BY-NC-ND">
</a>
"""

licenses = {'CC-BY-NC-ND': stdlicense }


def beautifyId(s):
    """Turn a string into something resembling a headline.
       Method: Split on all spaces and underscores, then capitalize
               every piece, then return the joined parts.
    """
    print "beautifyId(%s)" % s
    shards = [ c.capitalize() for c in re.split('[-_ ]', s) ]
    print "  crumbs = ", shards
    return " ".join(shards)


def getVideoList(path):
    """Get all videos in the specified directory"""
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IVideoConfiguration)
    vroot = settings.fspath
    prefix = ""
    if path.startswith(vroot) and path != vroot:
        prefix = path[len(vroot):]
        prefix = prefix.strip('/')
    allfiles = [ f[:f.find('.metadata')] for f in os.listdir(path) if f.endswith('.metadata') and f != '.metadata' ]
    result = {}
    for element in allfiles:
        result[os.path.join(prefix, element)] = beautifyId(element)
    return result

def addAllVideos(site, folder, fs_path, rights, options):
    """Add all videos found in the fs_path to the site."""
    parts = folder.split('/')
    target = site

    if options.publish:
        wft = getToolByName(site, 'portal_workflow')
    for part in parts:
        if part not in target.keys():
            target.invokeFactory('Folder', id=part, title=part)
        target = target[part]
    # issue #490:
    if options.layout:
        target.setLayout(options.layout)
    else:
        target.setLayout('videogallery')
    videos = getVideoList(fs_path)      # a dictionary
    for video in videos:
        newid = video[video.rfind('/')+1:]
        nv_id = target.invokeFactory('on.video.Video', id=newid, title=videos[video], filename = video)
        newvideo = target[nv_id]
        if rights:
            newvideo.body = RichTextValue('<p class="licenseimage">' + rights + '</p>')
        newvideo.setExcludeFromNav(True)
        if options.publish:
            wft.doActionFor(newvideo, 'publish')

### system integration boilerplate:

def get_app():
    frame = sys._getframe(2)
    return frame.f_locals.get('app')


def setup_parser():
    parser = optparse.OptionParser(
        usage="usage: ./bin/instance run ./bin/%prog [options] portal_path filesystem_path")
    parser.add_option(
        '-f', '--folder', dest="folder", default="",
        help="Which folder to import into (default: use an auto-generated name)")
    parser.add_option(
        '-l', '--license', dest="licensekey", default="CC-BY-NC-ND", action='store',
        help="""License string (default: CC-BY-NC-ND). If you want to use something else, specify the full required HTML code. If you want no license, specify NONE.""")
    parser.add_option(
        '-L', '--Layout', dest="layout", default="videogallery", action='store',
        help="""License string (default: CC-BY-NC-ND). If you want to use something else, specify the full required HTML code. If you want no license, specify NONE.""")
    parser.add_option(
        '-p', '--publish', dest="publish", default=False, action='store_true',
        help="Immediately publish all videos (they are likely to not be elegantly named)")
    return parser


### MAIN:

def main(app=None, instance_path=None):
    parser = setup_parser()
    options, args = parser.parse_args()
    global site

    if len(args) != 2:
        parser.print_help()
        sys.exit(1)
        return

    if app is None:
        app = get_app()
    try:
        instance_path = args[0]
        fs_path = args[1]
    except:
        parser.print_help()
        sys.exit(2)

    #folder = "imported-videos-%s" % datetime.now().strftime("%s")
    folder = 'imported-videos'
    licensekey = 'CC-BY-NC-ND'

    if not os.path.isdir(fs_path):
        parser.print_help()
        sys.exit(1)

    try:
        portal = app.unrestrictedTraverse(instance_path)
    except:
        print "The specified Plone site does not seem to exist, bailing out."
        parser.print_help()
        sys.exit(1)

    setSite(portal)
    site = portal

    if options.licensekey in licenses:
        rights = licenses[options.licensekey]
    elif options.licensekey != "NONE":
        rights = options.licensekey
    else:
        rights = None

    addAllVideos(site, folder, fs_path, rights, options)

    transaction.commit()
