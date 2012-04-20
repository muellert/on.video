from Acquisition import aq_inner

from zope import schema
from zope.interface import implements
from zope.formlib import form
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from on.video import _

class IFeaturedVideos(IPortletDataProvider):

    title = schema.TextLine(title=u'Title',
                            description=u'',
                            max_length=40, 
                            required=True,
                            default=u'Our Best Videos')

    entries = schema.Int(title=_(u'Number of Videos to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=3)


class Assignment(base.Assignment):
    implements(IFeaturedVideos)

    title = u'Our Best Videos'
    entries = 3
    
    def __init__(self, title=u'Our Best Videos', entries=3):
        self.title = title
        self.entries = entries

    @property
    def title(self):
        return self.title


class AddForm(base.AddForm):
    form_fields = form.Fields(IFeaturedVideos)
    label = u"Add Portlet for Featured Videos"
    description = u"Configure the portlet."

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IFeaturedVideos)
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

    @property
    def available(self):
        """Show the portlet only if there are one or more elements."""
        return not len(self._data())

    def featuredvideos(self):
        return self._data()

    @memoize
    def _data(self):
        limit = self.data.entries
        return cat(object_provides=IVideo.__identifier__,sort_on='effective',sort_order='ascending')[:limit]