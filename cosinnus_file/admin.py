# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from cosinnus_file.models import FileEntry


class FileEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'group', 'uploaded_date', 'uploaded_by')
    search_fields = ('name', 'note')


admin.site.register(FileEntry, FileEntryAdmin)
