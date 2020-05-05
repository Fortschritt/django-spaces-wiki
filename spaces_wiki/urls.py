from django.conf.urls import url, include
from wiki.core.utils import get_class_from_str
from wiki.urls import WikiURLPatterns, get_pattern as get_wiki_pattern
from wiki.views import article
from spaces.urls import space_patterns



from . import views

#app_name = 'spaces_wiki'

class SpaceWikiURLPatterns(WikiURLPatterns):
    """
        for subclassing and extending the views of django-wiki
    """
    article_view_class = views.SpaceArticleView
    article_create_view_class = views.SpaceCreate
    article_delete_view_class = views.SpaceDelete
    article_deleted_view_class = views.SpaceDeleted
    article_dir_view_class = views.SpaceDir
    article_edit_view_class = views.SpaceEdit
    article_preview_view_class = views.SpacePreview
    article_history_view_class = views.SpaceHistory
    article_settings_view_class = views.SpaceSettings
    article_source_view_class = views.SpaceSource
    article_plugin_view_class = views.SpacePlugin
    revision_change_view_class = views.SpaceChangeRevisionView
    root_view_class = views.SpaceIndex

    def get_root_urls(self):
        urlpatterns = [
            url('^$',
#                self.article_dir_view_class.as_view(),
                self.root_view_class.as_view(),
                name='root',
                kwargs={'path': ''}),
# Disabled for now
#            url('^_search/$',
#                get_class_from_str(self.search_view_class).as_view(),
#                name='search'),
            url('^_revision/diff/(?P<revision_id>[0-9]+)/$',
                self.article_diff_view,
                name='diff'),
        ]
        return urlpatterns


spaces_wiki_url_patterns = space_patterns(
        url(r'^notes/', get_wiki_pattern(
        namespace=None,
        url_config_class=SpaceWikiURLPatterns
        )
    ),
)

# dirty hack to prevent code duplication:
# django-wiki's decorator get_article() has hardcoded 'wiki' namespaces
# for redirects.
# We insert those urlpaths manually so that we can still provide the same 
# app_name pattern ('spaces_<pluginname>') as all the other Spaces plugins
# while keeping things mostly DRY.
wiki_url_patterns = space_patterns(
    url('^notes/(?P<path>.+/|)$', views.SpaceArticleView.as_view(), name='get'),
    url('^notes/(?P<path>.+/|)_create/$', views.SpaceCreate.as_view(), name='create'),
    url('^notes/(?P<path>.+/|)_deleted/$', views.SpaceDeleted.as_view(), name='deleted'),
)


app_name="spaces_wiki"
urlpatterns = (
    # regular views in spaces_wiki namespace
    url(r'', include((spaces_wiki_url_patterns, 'spaces_wiki'))),
    # some additional views for hardcoded 'wiki' namespace
    url(r'', include((wiki_url_patterns, 'wiki'))),
)


