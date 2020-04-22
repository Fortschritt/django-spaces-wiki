from django.conf import settings
from django.utils.translation import ugettext_noop as _

def create_notice_types(sender, **kwargs):
    if "pinax.notifications" in settings.INSTALLED_APPS:
        from spaces_notifications.utils import register_notification
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