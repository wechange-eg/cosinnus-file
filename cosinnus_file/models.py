# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import exists, isfile, join

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from cosinnus.utils.functions import unique_aware_slugify
from cosinnus.models.tagged import BaseTaggableObjectModel
from cosinnus_file.managers import FileEntryManager

import hashlib, uuid, time

@python_2_unicode_compatible

def get_hashed_filename(instance, filename):
    instance._sourcefilename = filename
    path = 'cosinnus_files' + '/' + str(instance.group_id) + time.strftime('/%Y/%m')
    newfilename = hashlib.sha1('%s%d%s' % (str(uuid.uuid4()), instance.group_id, filename)).hexdigest()
    return join(path, newfilename)


class FileEntry(BaseTaggableObjectModel):
    '''
        Model for uploaded files.
        FIles are saved under 'cosinnus_files/groupid/Year/Month/hashedfilename'
    '''
    SORT_FIELDS_ALIASES = [('name', 'name'), ('uploaded_date', 'uploaded_date'), ('uploaded_by', 'uploaded_by')]

    name = models.CharField(_(u'Name'), blank=False, null=False, max_length=50)
    note = models.TextField(_(u'Note'), blank=True, null=True)
    file = models.FileField(_(u'File'), blank=True, null=True,
                            max_length=250, upload_to=get_hashed_filename)#'files/%Y/%m/%d')
    isfolder = models.BooleanField(blank=False, null=False, default=False)
    path = models.CharField(_(u'Path'), blank=False, null=False, default='/', max_length=100)
    
    _sourcefilename = models.CharField(blank=False, null=False, default='download', max_length=100)
    
    
    uploaded_date = models.DateTimeField(_(u'Uploaded on'), default=now)
    uploaded_by = models.ForeignKey(User, verbose_name=_(u'Uploaded by'),
                                    on_delete=models.PROTECT,
                                    related_name='files')

    objects = FileEntryManager()
    
    @property
    def sourcefilename(self):
        return self._sourcefilename

    class Meta:
        ordering = ['-uploaded_date', 'name']
        verbose_name = _('Cosinnus File')
        verbose_name_plural = _('Cosinnus Files')

    def __str__(self):
        return self.name
    
    def clean(self):
        # if we are creating a file, require an uploaded file (not required for folders)
        if not self.isfolder and self.file.name is None:
            raise ValidationError(_(u'No files selected.'))
    
    def save(self, *args, **kwargs):
        if not self.slug:
            unique_aware_slugify(self, slug_source='name', slug_field='slug', group=self.group)
        if self.path[-1] != '/':
            self.path += '/'
        super(FileEntry, self).save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {'group': self.group.slug,
                  'slug': self.slug}
        return reverse('cosinnus:file:file', kwargs=kwargs)


@receiver(post_delete, sender=FileEntry)
def post_file_delete(sender, instance, **kwargs):
    if instance.file:
        path = instance.file.path
        if exists(path) and isfile(path):
            instance.file.delete(False)
