# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms.models import ModelForm

from cosinnus_file.models import FileEntry


class FileForm(ModelForm):

    class Meta:
        model = FileEntry
        fields = ('title', 'file', 'note', 'tags')

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # hide the file upload field on folders, and set the folder flag
        if instance and instance.isfolder or 'initial' in kwargs and 'isfolder' in kwargs['initial'] and kwargs['initial']['isfolder']:
            del self.fields['file']
            instance.isfolder = True

    def clean_isfolder(self):
        instance = getattr(self, 'instance', None)
        if instance:
            return self.cleaned_data['isfolder']

    def clean_file(self):
        fileupload = self.cleaned_data['file']
        if fileupload:
            instance = getattr(self, 'instance', None)
            if instance:
                instance.mimetype = fileupload.content_type
                print(instance.mimetype)
        return fileupload


class FileListForm(forms.Form):
    select = forms.MultipleChoiceField(required=False)  # required=False to handle this validation in the view
