from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateResponseMixin
from wiki.conf import settings
from wiki.core.plugins import registry
import wiki.views.mixins as wiki_mixins
from .decorators import article_owner_or_admin_required, article_owner_or_admin_required_for_restore

def is_root(article):
    """
        Is the given article the root article? Returns True/False
    """
    return (article.urlpath_set.first().level == 0)

class SpaceArticleMixin(TemplateResponseMixin):

    """ Gets children like wiki.views.mixins.ArticleMixin, but this variant is
    Space-aware.
    """

    def dispatch(self, request, article, *args, **kwargs):
        if not is_root(article) and \
            article.wikiarticle.wiki.space != request.SPACE:
            raise Http404(_('Article does not exist'))

        # only get children of the same space (mostly relevant for root)
        self.children_slice = []
        if settings.SHOW_MAX_CHILDREN > 0:
            try:
                for child in self.article.get_children(
                        max_num=settings.SHOW_MAX_CHILDREN +
                        1,
                        articles__article__current_revision__deleted=False,
                        articles__article__wikiarticle__wiki__space=\
                            request.SPACE,
                        user_can_read=request.user):
                    self.children_slice.append(child)
            except AttributeError as e:
#                log.error(
#                    "Attribute error most likely caused by wrong MPTT version. Use 0.5.3+.\n\n" +
#                    str(e))
                raise
        return super(SpaceArticleMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['children_slice'] = self.children_slice[:20]
        kwargs['children_slice_more'] = len(self.children_slice) > 20

        return kwargs


class ArticlePermissionMixin(object):
    """
    Deny access if user doesn't have sufficient permissions for
    editing wiki articles.
    """
    @method_decorator(article_owner_or_admin_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ArticlePermissionMixin, self).dispatch(request, *args, **kwargs)

class ArticleRestorePermissionMixin(object):
    """
    Deny access if user doesn't have sufficient permissions for
    editing wiki articles.
    """
    @method_decorator(article_owner_or_admin_required_for_restore)
    def dispatch(self, request, *args, **kwargs):
        return super(ArticleRestorePermissionMixin, self).dispatch(request, *args, **kwargs)

    
