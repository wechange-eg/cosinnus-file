# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import uuid

from os.path import exists, isfile, join
import os, shutil

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from cosinnus.conf import settings
from cosinnus.models import BaseTaggableObjectModel

from cosinnus_file.managers import FileEntryManager


def get_hashed_filename(instance, filename):
    instance._sourcefilename = filename
    time = now()
    path = join('cosinnus_files', force_text(instance.group_id),
        force_text(time.year), force_text(time.month))
    name = '%s%d%s' % (force_text(uuid.uuid4()), instance.group_id, filename)
    newfilename = hashlib.sha1(name.encode('utf-8')).hexdigest()
    return join(path, newfilename)


class FileEntry(BaseTaggableObjectModel):
    """
    Model for uploaded files.

    Files are saved under 'cosinnus_files/groupid/Year/Month/hashedfilename'
    """
    SORT_FIELDS_ALIASES = [('title', 'title'), ('uploaded_date', 'uploaded_date'), ('uploaded_by', 'uploaded_by')]

    note = models.TextField(_('Note'), blank=True, null=True)
    file = models.FileField(_('File'), blank=True, null=True,
                            max_length=250, upload_to=get_hashed_filename)
    isfolder = models.BooleanField(blank=False, null=False, default=False)
    path = models.CharField(_('Path'), blank=False, null=False, default='/', max_length=100, editable=False)

    _sourcefilename = models.CharField(blank=False, null=False, default='download', max_length=100)

    uploaded_date = models.DateTimeField(_('Uploaded on'), default=now)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Uploaded by'),
                                    on_delete=models.PROTECT,
                                    related_name='files')
    mimetype = models.CharField(_('Path'), blank=True, null=True, default='', max_length=50, editable=False)

    objects = FileEntryManager()

    @property
    def get_static_image_url(self):
        '''
            This serves as a helper function to display Cosinnus Image Files on the webpage.
            The image file is copied to a general image folder in cosinnus_files, so the true image
            path is not shown to the client.
            This function copies the image to its new path (if necessary) and returns
            the URL for the image to be displayed on the page. (Ex: '/media/cosinnus_files/images/dca2b30b1e07ed135c24d7dbd928e37523b474bb.jpg') 
        '''
        if not self.is_image:
            return ''

        mediapath = join('cosinnus_files', 'images')
        mediapath_local = join(settings.MEDIA_ROOT, mediapath)
        if not os.path.exists(mediapath_local):
            os.makedirs(mediapath_local)

        image_filename = self.file.path.split(os.sep)[-1] + '.' + self.sourcefilename.split('.')[-1]
        imagepath_local = join(mediapath_local, image_filename)
        if not os.path.exists(imagepath_local):
            shutil.copy(self.file.path, imagepath_local)

        return join(settings.MEDIA_URL, mediapath, image_filename)

    @property
    def is_image(self):
        if not self.file or not self.mimetype:
            return False
        return self.mimetype.startswith('image/')

    @property
    def sourcefilename(self):
        return self._sourcefilename

    class Meta:
        ordering = ['-uploaded_date', 'title']
        verbose_name = _('Cosinnus File')
        verbose_name_plural = _('Cosinnus Files')

    def __str__(self):
        return '%s (%s%s)' % (self.title, self.path, '' if self.isfolder else self.sourcefilename)

    def clean(self):
        # if we are creating a file, require an uploaded file (not required for folders)
        if not self.isfolder and self.file.name is None:
            raise ValidationError(_('No files selected.'))

    def save(self, *args, **kwargs):
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
