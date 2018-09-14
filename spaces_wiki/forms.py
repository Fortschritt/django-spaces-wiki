import itertools
from django import forms
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from wiki import models
from wiki.forms import CreateForm, DeleteForm

class SpaceCreateForm(CreateForm):
    """
        Variant of wiki.forms.CreateForm. Makes slug optional and automatically
        generates unique slug if empty or already existing.
    """

    slug = forms.SlugField(
        label=_('Slug'),
        help_text=_(
            "This will be the address where your article can be found. Use only alphanumeric characters and - or _. Note that you cannot change the slug after creating the article."),
        max_length=models.URLPath.SLUG_MAX_LENGTH,
        required=False)

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            title = self.cleaned_data['title'] if 'title' in self.cleaned_data else ''
            slug = title
        else:
            if slug.startswith("_"):
                raise forms.ValidationError(
                _('A slug may not begin with an underscore.'))
            if slug == 'admin':
                raise forms.ValidationError(
                _("'admin' is not a permitted slug name."))
        max_length = models.URLPath.SLUG_MAX_LENGTH
        start_slug = slug = slugify(slug)[:max_length]
        for x in itertools.count(1):
            if not models.URLPath.objects.filter(
                slug__iexact=slug,
                parent=self.urlpath_parent).exists():
                break
            slug = '%s%d' % (start_slug[:max_length - len(str(x))], x)
        return slug

class SpaceDeleteForm(DeleteForm):

    confirm = None
    purge = None

    def clean(self):
        cd = self.cleaned_data
        if cd['revision'] != self.article.current_revision:
            raise forms.ValidationError(
                _(
                    'While you tried to delete this article, it was modified. TAKE CARE!'))
        return cd
