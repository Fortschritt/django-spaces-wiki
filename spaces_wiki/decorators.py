from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from wiki.models.urlpath import URLPath
from collab.util import is_owner_or_admin


def article_owner_or_admin_required(func):
    """
    method decorator raising 403 if user is neither the owner of the file
    nor a space administrator or manager.
    """
    def _decorator(self, *args, **kwargs):
        if 'path' in kwargs.keys():
            slug = kwargs['path']
            slug = slug[:-1] if slug[-1] == '/' else slug
        else:
            slug = None
        obj = get_object_or_404(URLPath, slug=slug)
        if self.user and self.user.is_authenticated():
            is_allowed = is_owner_or_admin(
                self.user,
                obj.article.owner,
                self.SPACE
            )
            if is_allowed:
                return func(self, *args, **kwargs)
        raise PermissionDenied
    return _decorator

def article_owner_or_admin_required_for_restore(func):
    """
    same as article_owner_or_admin_required, but:
    * allows accessing the view as long as 'restore' is not in request.GETm
      preventing undeleting articles the user hasn't authored.
    """
    def _decorator(self, *args, **kwargs):
        if 'path' in kwargs.keys():
            slug = kwargs['path']
            slug = slug[:-1] if slug[-1] == '/' else slug
        else:
            slug = None
        obj = get_object_or_404(URLPath, slug=slug)
        if self.user and self.user.is_authenticated():
            is_allowed = is_owner_or_admin(
                self.user,
                obj.article.owner,
                self.SPACE
            )
            no_restore = 'restore' not in self.GET
            if is_allowed or no_restore:
                return func(self, *args, **kwargs)
        raise PermissionDenied
    return _decorator
