from django.apps import AppConfig
from django.db.models.signals import post_migrate

from collab.util import db_table_exists, db_table_column_exists
from spaces_wiki.signals import create_notice_types

class SpacesWikiConfig(AppConfig):
    name = 'spaces_wiki'

    def ready(self):
        # django-wiki needs a root page.
        # create_root emulates get_or_create, so this should only create 
        # a new root file if none exists yet.
        from wiki.models import URLPath

        if db_table_exists('django_site'):
            # the following condition was needed for a wiki migration of wiki 0.3.1
            if db_table_column_exists('wiki_urlpath', 'moved_to_id'):
                URLPath.create_root()

        # activate activity streams for WikiArticle
        from actstream import registry
        from .models import WikiArticle
        registry.register(WikiArticle)

        # register a custom notification
        """
        from spaces_notifications.utils import register_notification
        from django.utils.translation import ugettext_noop as _
        register_notification(
            'spaces_wiki_create',
            _('A new article has been published.'),
            _('A new article has been published.')
        )
        register_notification(
            'spaces_wiki_modify',
            _('An article has been modified.'),
            _('An article has been modified.')
        )
        """
        post_migrate.connect(create_notice_types, sender=self)