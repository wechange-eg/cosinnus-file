# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os
import shutil
import uuid

from os.path import exists, isfile, join

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
from cosinnus.models.tagged import BaseHierarchicalTaggableObjectModel


def get_hashed_filename(instance, filename):
    instance._sourcefilename = filename
    time = now()
    path = join('cosinnus_files', force_text(instance.group_id),
        force_text(time.year), force_text(time.month))
    name = '%s%d%s' % (force_text(uuid.uuid4()), instance.group_id, filename)
    newfilename = hashlib.sha1(name.encode('utf-8')).hexdigest()
    return join(path, newfilename)


class FileEntry(BaseHierarchicalTaggableObjectModel):
    """
    Model for uploaded files.

    Files are saved under 'cosinnus_files/groupid/Year/Month/hashedfilename'

    The content type for files is saved in self.mimetype. It finds a special application
    in defining whether a FileEntry is an image (self.is_image).

    Image-files are ~additionally~ copied to '/cosinnus_files/images/hashedfilename.<ext>'
    during the first request of self.static_image_url.
    This then returns that path in the images folder, so the image can be served from a
    publicly suitable location for http requests and so it also shows its file extension.
    The image-copy is deleted when the FileEntry is deleted (post_delete).

    """
    SORT_FIELDS_ALIASES = [('title', 'title'), ('created', 'created'), ('creator', 'creator')]

    note = models.TextField(_('Note'), blank=True, null=True)
    file = models.FileField(_('File'), blank=True, null=True,
                            max_length=250, upload_to=get_hashed_filename)

    _sourcefilename = models.CharField(blank=False, null=False, default='download', max_length=100)

    mimetype = models.CharField(_('Path'), blank=True, null=True, default='', max_length=50, editable=False)

    objects = FileEntryManager()

    @property
    def static_image_url(self):
        """
        This function copies the image to its new path (if necessary) and
        returns the URL for the image to be displayed on the page. (Ex:
        '/media/cosinnus_files/images/dca2b30b1e07ed135c24d7dbd928e37523b474bb.jpg')

        It is a helper function to display cosinnus image files on the webpage.

        The image file is copied to a general image folder in cosinnus_files,
        so the true image path is not shown to the client.

        """
        if not self.is_image:
            return ''
        media_image_path = self.get_media_image_path()

        # if image is not in media dir yet, copy it
        imagepath_local = join(settings.MEDIA_ROOT, media_image_path)
        if not exists(imagepath_local):
            shutil.copy(self.file.path, imagepath_local)

        media_image_path = media_image_path.replace('\\', '/')  # fix for local windows systems
        return join(settings.MEDIA_URL, media_image_path)

    @property
    def is_image(self):
        if not self.file or not self.mimetype:
            return False
        return self.mimetype.startswith('image/')

    @property
    def sourcefilename(self):
        return self._sourcefilename

    def get_media_image_path(self):
        """Gets the unique path for each image file in the media directory"""
        mediapath = join('cosinnus_files', 'images')
        mediapath_local = join(settings.MEDIA_ROOT, mediapath)
        if not exists(mediapath_local):
            os.makedirs(mediapath_local)
        image_filename = self.file.path.split(os.sep)[-1] + '.' + self.sourcefilename.split('.')[-1]
        return join(mediapath, image_filename)

    class Meta(BaseTaggableObjectModel.Meta):
        ordering = ['-created', 'title']
        verbose_name = _('Cosinnus File')
        verbose_name_plural = _('Cosinnus Files')

    def __init__(self, *args, **kwargs):
        super(FileEntry, self).__init__(*args, **kwargs)
        self._meta.get_field('creator').verbose_name = _('Uploaded by')
        self._meta.get_field('created').verbose_name = _('Uploaded on')

    def __str__(self):
        return '%s (%s%s)' % (self.title, self.path, '' if self.is_container else self.sourcefilename)

    def clean(self):
        # if we are creating a file, require an uploaded file (not required for folders)
        if not self.is_container and self.file.name is None:
            raise ValidationError(_('No files selected.'))

    def save(self, *args, **kwargs):
        if self.path[-1] != '/':
            self.path += '/'
        super(FileEntry, self).save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {'group': self.group.slug,
                  'slug': self.slug}
        return reverse('cosinnus:file:download', kwargs=kwargs)


@receiver(post_delete, sender=FileEntry)
def post_file_delete(sender, instance, **kwargs):
    """
    When the user deletes a FileEntry, delete the file on the disk,
    and delete the media-image copy of the file if it was an image.
    """
    if instance.file:
        # delete media image file if it existed
        if instance.is_image:
            imagepath_local = join(settings.MEDIA_ROOT, instance.get_media_image_path())
            if exists(imagepath_local):
                os.remove(imagepath_local)

        path = instance.file.path
        if exists(path) and isfile(path):
            instance.file.delete(False)


import django
if django.VERSION[:2] < (1, 7):
    from cosinnus_file import cosinnus_app
    cosinnus_app.register()
