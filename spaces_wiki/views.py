from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from actstream.signals import action as actstream_action
from guardian.mixins import PermissionRequiredMixin
from wiki.conf import settings
from wiki.decorators import get_article
from wiki.forms import EditForm, DeleteForm
from wiki.models import URLPath
import wiki.views.article as wiki_article

from collab.decorators import permission_required_or_403, space_admin_required
from spaces.models import SpacePluginRegistry
from spaces_notifications.mixins import NotificationMixin
from .forms import SpaceCreateForm, SpaceDeleteForm
from .models import SpacesWiki, WikiArticle, WikiPlugin
from .mixins import SpaceArticleMixin, ArticlePermissionMixin, ArticleRestorePermissionMixin

class WikiContextMixin(object):
    """
        Adds 
        * a complete list of articles to the context. Useful for
          displaying a table of contents for the wiki.
    """
    def get_context_data(self, **kwargs):
        context = super(WikiContextMixin, self).get_context_data(**kwargs)
        context["full_tree"] = URLPath.objects.filter(
            article__wikiarticle__wiki__space=self.request.SPACE
        )
        context['plugin_selected'] = WikiPlugin.name
        return context


class SpaceArticleView(WikiContextMixin, wiki_article.ArticleView, SpaceArticleMixin):
    template_name = 'spaces_wiki/view.html'

    @method_decorator(get_article(can_read=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish: method decorator pops 'article_id' and 'path', so we 
        # add them back to make muliple decorator calls possible
        # Using django guardian's PermissionRequiredMixin would be nicer,
        # but how to get request.SPACE to check permission against?
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path

        return super(SpaceArticleView,self).dispatch(
            request,
            article,
            *args,
            **kwargs
        )

    def get_context_data(self, **kwargs):
        kwargs = super(SpaceArticleView, self).get_context_data(**kwargs)
        kwargs['spaced_children_slice'] = self.children_slice
        return kwargs


class SpaceDir(WikiContextMixin, wiki_article.Dir, SpaceArticleMixin):

    @method_decorator(get_article(can_read=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceDir, self).dispatch(
            request, 
            article, 
            *args, 
            **kwargs
        )

    def get_queryset(self):
        children = super(SpaceDir, self).get_queryset()
        children = children.filter(article__wikiarticle__wiki__space=self.request.SPACE)
        return children


class SpaceDiffView(WikiContextMixin, wiki_article.DiffView, SpaceArticleMixin):
    pass

class SpaceIndex(SpaceDir):
    template_name="spaces_wiki/index.html"

class SpaceCreate(NotificationMixin, WikiContextMixin, wiki_article.Create, SpaceArticleMixin):
    template_name = "spaces_wiki/create.html"
    form_class = SpaceCreateForm
    notification_label = 'spaces_wiki_create'
    notification_send_manually = True

    @method_decorator(get_article(can_write=True, can_create=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceCreate, self).dispatch(
            request, 
            article, 
            *args, 
            **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(SpaceCreate, self).get_context_data(**kwargs)
        context['create_form'] = self.get_form(SpaceCreateForm)
        return context

    def form_valid(self, form):
        ret = super(SpaceCreate, self).form_valid(form)
        root_redirect = redirect('wiki:get','')
        if isinstance(ret, HttpResponseRedirect) and root_redirect.url != ret.url:
            # super().form_valid successfully created a new article,
            # now get the new article and create our own WikiArticle instance
            # for proper integration.
            new_article = self.newpath.article
            wiki = SpacesWiki.objects.get(space=self.request.SPACE)
            wiki_article = WikiArticle.objects.create(
                article = new_article,
                wiki = wiki
            )
            # create dashboard notification
            actstream_action.send(
                sender=self.request.user,
                verb=_("was created"),
                target=self.request.SPACE,
                action_object=wiki_article
            )
            # set title and link for notification mail
            self.notification_object_title = new_article
            self.notification_object_link = new_article.get_absolute_url()
            self.send_notification()
            
        return ret

class SpaceSettings(wiki_article.Settings):

    @method_decorator(get_article(can_read=True, deleted_contents=True))
    def dispatch(self, request, article, *args, **kwargs):
        # disabling this view
        raise PermissionDenied
    
class SpaceHistory(WikiContextMixin, wiki_article.History, SpaceArticleMixin):
    template_name = "spaces_wiki/history.html"

    @method_decorator(get_article(can_read=True, deleted_contents=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceHistory, self).dispatch(
            request,
            article,
            *args,
            **kwargs
        )

# Note: untested!
class SpacePlugin(wiki_article.Plugin):

    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, path=None, slug=None, **kwargs):
        return super(SpacePlugin,self).dispatch(
            request,
            path,
            slug,
            **kwargs
        )

class SpaceEdit(NotificationMixin, WikiContextMixin, wiki_article.Edit, SpaceArticleMixin):
    template_name="spaces_wiki/edit.html"
    notification_label = 'spaces_wiki_modify'

    @method_decorator(get_article(can_write=True, not_locked=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceEdit, self).dispatch(
            request, 
            article, 
            *args, 
            **kwargs)

    def form_valid(self, form):
        # set title and link for notification mail
        self.notification_object_title = self.article
        self.notification_object_link  = self.article.get_absolute_url()
        ret = super(SpaceEdit, self).form_valid(form)
        if isinstance(ret, HttpResponseRedirect):
            # super().form_valid successfully saved the article
            # create dashboard notification
            actstream_action.send(
                sender=self.request.user,
                verb=_("was modified"),
                target=self.request.SPACE,
                action_object=self.article.wikiarticle
            )

        return ret


    def get_context_data(self, **kwargs):
        context = super(SpaceEdit, self).get_context_data(**kwargs)
        # most probably the same bug as this: 
        # https://github.com/django-wiki/django-wiki/issues/497
        # if bug gets fixed in a proper way, the next line can be removed
        context['edit_form'] = self.get_form(EditForm)
        # set title and link for n12n mails
        context["object_title"] = self.article
        context["object_link"] = self.article.get_absolute_url()
        return context


class SpaceDelete(WikiContextMixin, wiki_article.Delete, SpaceArticleMixin):
    form_class = SpaceDeleteForm
    template_name = "spaces_wiki/delete.html"

    @method_decorator(get_article(can_write=True, not_locked=True, can_delete=True))
    #@method_decorator(permission_required_or_403('access_space'))
    @method_decorator(space_admin_required)
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceDelete, self).dispatch(
            request, 
            article, 
            *args, 
            **kwargs
        )

    def get_form(self, form_class=None):
        form = super(wiki_article.Delete, self).get_form(form_class=form_class)
        return form

    def form_valid(self, form):
        form.cleaned_data['purge'] = False
        return super(SpaceDelete, self).form_valid(form)

    def get_success_url(self):
        return redirect('spaces_wiki:root')

    def get_context_data(self, **kwargs):
        context = super(SpaceDelete, self).get_context_data(**kwargs)
        # most probably the same bug as this: 
        # https://github.com/django-wiki/django-wiki/issues/497
        # if bug gets fixed in a proper way, get_context_data can be removed
        context['delete_form'] = self.get_form(self.form_class)
        return context



class SpaceDeleted (WikiContextMixin, ArticleRestorePermissionMixin, wiki_article.Deleted):
    template_name = "spaces_wiki/deleted.html"
    
    @method_decorator(get_article(can_read=True, deleted_contents=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceDeleted, self).dispatch(
            request,
            article,
            *args,
            **kwargs
        )

class SpaceSource(WikiContextMixin, wiki_article.Source, SpaceArticleMixin):
    
    @method_decorator(get_article(can_read=True, deleted_contents=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch    
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceSource, self).dispatch(
            request,
            article,
            *args,
            **kwargs
        )

class SpacePreview(WikiContextMixin, wiki_article.Preview, SpaceArticleMixin):
    template_name = "spaces_wiki/preview_inline.html"
    
    @method_decorator(get_article(can_read=True, deleted_contents=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpacePreview,self).dispatch(
            request,
            article,
            *args,
            **kwargs
        )

# Note: untested
class SpaceChangeRevisionView(WikiContextMixin, wiki_article.ChangeRevisionView, SpaceArticleMixin):

    @method_decorator(get_article(can_write=True, not_locked=True))
    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, article, *args, **kwargs):
        # hackish, see SpaceArticleView.dispatch
        kwargs['article_id'] = article.id
        kwargs['path'] = kwargs['urlpath'].path
        return super(SpaceChangeRevisionView,self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_redirect_url(self, **kwargs):
        if self.urlpath:
            return reverse("spaces_wiki:get", kwargs={'path': self.urlpath.path})
        else:
            return reverse(
                'spaces_wiki:get',
                kwargs={
                    'article_id': self.article.id})


# dummy dict for translation strings
trans_strings = {
    1: _('A new revision of the article was successfully added.')
}