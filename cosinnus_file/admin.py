# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from cosinnus_file.models import FileEntry
from cosinnus.admin import BaseHierarchicalTaggableAdminMixin


class FileEntryAdmin(BaseHierarchicalTaggableAdminMixin, admin.ModelAdmin):
    list_display = BaseHierarchicalTaggableAdminMixin.list_display + ['sourcefilename']
    search_fields = BaseHierarchicalTaggableAdminMixin.search_fields + ['sourcefilename']

admin.site.register(FileEntry, FileEntryAdmin)
