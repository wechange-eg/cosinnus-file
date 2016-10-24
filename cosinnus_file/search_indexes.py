# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from haystack import indexes

from cosinnus.utils.search import BaseHierarchicalTaggableObjectIndex

from cosinnus_file.models import FileEntry


class FileEntryIndex(BaseHierarchicalTaggableObjectIndex, indexes.Indexable):

    def get_model(self):
        return FileEntry

