# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from haystack import indexes

from cosinnus.utils.search import BaseTaggableObjectIndex

from cosinnus_file.models import FileEntry


class FileEntryIndex(BaseTaggableObjectIndex, indexes.Indexable):
    note = indexes.CharField(model_attr='note', null=True)

    def get_model(self):
        return FileEntry

