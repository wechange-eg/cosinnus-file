# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms.models import ModelForm

from cosinnus_file.models import FileEntry
from django.forms import fields
from django.forms.fields import Field


class FileForm(ModelForm):

    class Meta:
        model = FileEntry
        fields = ('name', 'file', 'path', 'note', 'tags')
        
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['path'].widget.attrs['readonly'] = True
            # hide the file upload field on folders, and set the folder flag
            if instance.isfolder == True or 'initial' in kwargs and 'isfolder' in kwargs['initial'] and kwargs['initial']['isfolder']:
                del self.fields['file']
                instance.isfolder = True
                
    def clean_path(self):
        instance = getattr(self, 'instance', None)
        if instance:
            return self.cleaned_data['path']
        
    def clean_isfolder(self):
        instance = getattr(self, 'instance', None)
        if instance:
            return self.cleaned_data['isfolder']
        

class FileListForm(forms.Form):
    select = forms.MultipleChoiceField(required=False)  # required=False to handle this validation in the view
