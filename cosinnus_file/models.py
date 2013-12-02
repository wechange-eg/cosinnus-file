# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import exists, isfile

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from cosinnus.utils.functions import unique_aware_slugify
from cosinnus.models.tagged import BaseTaggableObjectModel

from cosinnus_file.managers import FileEntryManager


@python_2_unicode_compatible
class FileEntry(BaseTaggableObjectModel):

    SORT_FIELDS_ALIASES = [('name', 'name'), ('uploaded_date', 'uploaded_date'), ('uploaded_by', 'uploaded_by')]

    name = models.CharField(_(u'Name'), blank=False, null=False, max_length=50)
    note = models.TextField(_(u'Note'), blank=True, null=True)
    file = models.FileField(_(u'File'), blank=False, null=False,
                            max_length=250, upload_to='files/%Y/%m/%d')
    uploaded_date = models.DateTimeField(_(u'Uploaded on'), default=now)
    uploaded_by = models.ForeignKey(User, verbose_name=_(u'Uploaded by'),
                                    on_delete=models.PROTECT,
                                    related_name='files')

    objects = FileEntryManager()

    class Meta:
        ordering = ['-uploaded_date', 'name']
        verbose_name = _('File')
        verbose_name_plural = _('Files')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            unique_aware_slugify(self, slug_source='name', slug_field='slug', group=self.group)
        super(FileEntry, self).save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {'group': self.group.slug,
                  'slug': self.slug}
        return reverse('cosinnus:file:file', kwargs=kwargs)


@receiver(post_delete, sender=FileEntry)
def post_file_delete(sender, instance, **kwargs):
    path = instance.file.path
    if exists(path) and isfile(path):
        instance.file.delete(False)
