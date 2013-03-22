from Acquisition import aq_inner
from AccessControl import getSecurityManager

from zope import schema
from zope.interface import implements
from zope.formlib import form
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from on.video import _
from on.video.video import IVideo, ViewThumbnail

class IFeaturedVideos(IPortletDataProvider):

    header = schema.TextLine(title=u'Portlet Title',
                            description=u'Title of the rendered Portlet',
                            max_length=40, 
                            required=True)

    target_collection = schema.Choice(
        title=_(u"Target collection"),
        description=_(u"Search for a collection that contains your videos."),
        required=True,
        source=SearchableTextSourceBinder(
            {'portal_type': ('Collection')},
            default_query='path:'))

    entries = schema.Int(title=_(u'Number of Videos to display'),
                       description=_(u'How many items to list.'
                                     u'To have the portlet scroll through the thumbnails, '
                                     u'you need a collection with at least 4 videos.'),
                       required=True,
                       default=1)

    show_more = schema.Bool(
        title=_(u"Show more... link"),
        description=_(u"If enabled, a more... link will appear in the footer "
                      u"of the portlet, linking to the underlying "
                      u"Collection."),
        required=True,
        default=True)

class Assignment(base.Assignment):
    implements(IFeaturedVideos)

    def __init__(self,
                 header=u"",
                 target_collection=None,
                 entries=1,
                 show_more=True):
        self.header = header
        self.target_collection = target_collection
        self.entries = entries
        self.show_more = show_more

    @property
    def title(self):
        return self.header


class AddForm(base.AddForm):
    form_fields = form.Fields(IFeaturedVideos)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    
    label = u"Add Portlet for Featured Videos"
    description = u"Configure the portlet."

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IFeaturedVideos)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    label = u"Edit Portlet for Featured Videos"
    description = u"Configure the portlet."


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('featuredvideos.pt') 

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.cat = plone_tools.catalog()

    def render(self):
        return self._template()

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    def get_results(self):
        results = []
        collection = self.collection()
        if collection is not None:
            limit = self.data.entries
            results = collection.queryCatalog(batch=False)

            results = results[:limit]
        return results

    @memoize
    def get_gallery_pictures(self):
        gallery = None
        pictures = []
        num_pictures = self.data.entries
        gallery = self.get_results()
        for i in gallery:
            iobj = i.getObject()
            if iobj.portal_type == 'on.video.Video':
                rdict = {'url': i.getURL()}
                vth = ViewThumbnail(iobj, iobj)            
                rdict['thumbnail'] = vth.thumbnail()
                rdict['title'] = vth.title()
                rdict['id'] = vth.id
                pictures.append(rdict)
        return pictures

    @memoize
    def collection(self):
        collection_path = self.data.target_collection
        # print "COLLECTION PATH: " +str(collection_path)

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]

        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(collection_path, unicode):
            # restrictedTraverse accepts only strings
            collection_path = str(collection_path)

        result = portal.unrestrictedTraverse(collection_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result
        
    @property
    def available(self):
        """Show the portlet only if there are one or more elements."""
        if len(self.collection()) > 0:
               return True
        return False

    """
    def viewthumb(self):
        res = self.get_gallery_pictures()
        # import pdb; pdb.set_trace()
        for i in res:
            rdict = {'url': i.getURL()}
            obj = i.getObject()
            vth = ViewThumbnail(obj, obj)            
            rdict['thumbnail'] = vth.thumbnail()
            rdict['title'] = vth.title()
            rlist.append(rdict)

        return rlist 
    """

        
