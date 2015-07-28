# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from cosinnus_file.models import FileEntry


class FileEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_container', 'path', 'file', 'group', 'created', 'creator')
    list_filter = ('group', )
    search_fields = ('title', 'note')


admin.site.register(FileEntry, FileEntryAdmin)
