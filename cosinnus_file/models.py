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
from django.utils.translation import ugettext_lazy as _, pgettext

from cosinnus.conf import settings
from cosinnus.models import BaseTaggableObjectModel

from cosinnus_file.managers import FileEntryManager
from cosinnus.models.tagged import BaseHierarchicalTaggableObjectModel
from cosinnus.utils.permissions import filter_tagged_object_queryset_for_user
from cosinnus.utils.urls import group_aware_reverse
from cosinnus_file import cosinnus_notifications
from django.contrib.auth import get_user_model
from cosinnus.utils.files import get_cosinnus_media_file_folder
from cosinnus.utils.functions import unique_aware_slugify
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError


def get_hashed_filename(instance, filename):
    instance._sourcefilename = filename
    time = now()
    path = join(get_cosinnus_media_file_folder(), 'files', force_text(instance.group_id),
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
    _filesize = models.IntegerField(blank=True, null=True, default='0')
    
    mimetype = models.CharField(_('Path'), blank=True, null=True, default='', max_length=50)

    objects = FileEntryManager()
    
    @property
    def filesize(self):
        if not self.file or not self._filesize:
            return 0
        return self._filesize

    def static_image_url(self, size=None, filename_modifier=None):
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
        if not size:
            size = settings.COSINNUS_IMAGE_MAXIMUM_SIZE_SCALE
            
        # the modifier can be used to save images of different sizes
        media_image_path = self.get_media_image_path(filename_modifier=filename_modifier)

        # if image is not in media dir yet, resize and copy it
        imagepath_local = join(settings.MEDIA_ROOT, media_image_path)
        if not exists(imagepath_local):
            thumbnailer = get_thumbnailer(self.file)
            try:
                thumbnail = thumbnailer.get_thumbnail({
                    'crop': 'scale',
                    'size': size,
                })
            except InvalidImageFormatError:
                raise
            
            if not thumbnail:
                return ''
            shutil.copy(thumbnail.path, imagepath_local)
        
        media_image_path = media_image_path.replace('\\', '/')  # fix for local windows systems
        return join(settings.MEDIA_URL, media_image_path)
    
    
    def static_image_url_thumbnail(self):
        return self.static_image_url(settings.COSINNUS_IMAGE_THUMBNAIL_SIZE_SCALE, 'small')
    
    @property
    def is_image(self):
        if not self.file or not self.mimetype:
            return False
        return self.mimetype.startswith('image/')

    @property
    def sourcefilename(self):
        return self._sourcefilename

    def get_media_image_path(self, filename_modifier=None):
        """Gets the unique path for each image file in the media directory"""
        mediapath = join('cosinnus_files', 'image_thumbnails')
        mediapath_local = join(settings.MEDIA_ROOT, mediapath)
        if not exists(mediapath_local):
            os.makedirs(mediapath_local)
        filename_modifier = '_' + filename_modifier if filename_modifier else ''
        image_filename = self.file.path.split(os.sep)[-1] + filename_modifier + '.' + self.sourcefilename.split('.')[-1]
        return join(mediapath, image_filename)

    class Meta(BaseTaggableObjectModel.Meta):
        ordering = ['-created', 'title']
        verbose_name = _('File')
        verbose_name_plural = _('Files')

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
        if len(self.mimetype) > 50:
            self.mimetype = self.mimetype[:50]    
        created = bool(self.pk) == False
        super(FileEntry, self).save(*args, **kwargs)
        if created and not self.is_container:
            # todo was created
            cosinnus_notifications.file_created.send(sender=self, user=self.creator, obj=self, audience=get_user_model().objects.filter(id__in=self.group.members).exclude(id=self.creator.pk))
        

    def get_absolute_url(self):
        kwargs = {'group': self.group,
                  'slug': self.slug}
        return group_aware_reverse('cosinnus:file:download', kwargs=kwargs)
    
    def get_delete_url(self):
        kwargs = {'group': self.group,
                  'slug': self.slug}
        return group_aware_reverse('cosinnus:file:delete', kwargs=kwargs)
    
    @classmethod
    def get_current(self, group, user):
        """ Returns a queryset of the current upcoming events """
        qs = FileEntry.objects.filter(group=group)
        if user:
            qs = filter_tagged_object_queryset_for_user(qs, user)
        return qs.filter(is_container=False)


def get_or_create_attachment_folder(group):
    attachment_folder = None
    try:
        attachment_folder = FileEntry.objects.get(is_container=True, group=group,
              special_type='attached')
    except FileEntry.DoesNotExist:
        pgettext('special_folder_type', 'Attachments') # leave this for i18n to find!
        attachment_folder = FileEntry(title='Attachments', is_container=True, group=group,
              special_type='attached')
        unique_aware_slugify(attachment_folder, 'title', 'slug')
        attachment_folder.path = '/%s/' % attachment_folder.slug
        attachment_folder.save()
    return attachment_folder


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
