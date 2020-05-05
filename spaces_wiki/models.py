from django.db import models
from django.utils.translation import ugettext_lazy as _
from wiki.models.article import Article
from spaces.models import Space,SpacePluginRegistry, SpacePlugin, SpaceModel

# Create your models here.

class SpacesWiki(SpacePlugin):
    """
    Wiki/Note taking plugin for Spaces. This only provides general 
    metadata per space. Content is available in WikiArticle instances.
    """
    # active field (boolean) inherited from SpacePlugin
    # space field (foreignkey) inherited from SpacePlugin
    reverse_url = 'spaces_wiki:root'

class WikiArticle(SpaceModel):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    wiki = models.ForeignKey(SpacesWiki, on_delete=models.CASCADE)

    spaceplugin_field_name = "wiki"

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')

    def __str__(self):
        return self.article.__str__() 

    def get_absolute_url(self):
        return self.article.get_absolute_url()

class WikiPlugin(SpacePluginRegistry):
    """
    Provide a wiki plugin for Spaces. This makes the SpacesWiki class visible 
    to the plugin system.
    """
    name = 'spaces_wiki'
    title = _('Notebook')
    plugin_model = SpacesWiki
    searchable_fields = (WikiArticle, ('article__current_revision__title', 'article__current_revision__content'))