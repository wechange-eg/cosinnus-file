# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.core.files.uploadedfile import UploadedFile

from cosinnus.forms.group import GroupKwargModelFormMixin
from cosinnus.forms.tagged import get_form, BaseTaggableObjectForm
from cosinnus.forms.user import UserKwargModelFormMixin

from cosinnus_file.models import FileEntry


class _FileForm(GroupKwargModelFormMixin, UserKwargModelFormMixin,
                BaseTaggableObjectForm):

    class Meta:
        model = FileEntry
        fields = ('title', 'file', 'note')

    def __init__(self, *args, **kwargs):
        super(_FileForm, self).__init__(*args, **kwargs)
        # hide the file upload field on folders, and set the folder flag
        if self.instance.is_container or \
                'initial' in kwargs and 'is_container' in kwargs['initial'] and \
                kwargs['initial']['is_container']:
            del self.fields['file']
            self.instance.is_container = True

    def clean_is_container(self):
        if self.instance:
            return self.cleaned_data['is_container']

    def clean_file(self):
        fileupload = self.cleaned_data['file']
        if fileupload and isinstance(fileupload, UploadedFile):
            max_length = self._meta.model._meta.get_field('_sourcefilename').max_length
            name = fileupload._name
            # shorten file name before its file suffix if it is too long
            if len(name) > max_length:
                if '.' in fileupload._name:
                    filename, suffix = name.rsplit('.', 1)
                    test = '.'.join([filename[:max_length-len(suffix)-1], suffix])
                    fileupload._name = test
                else:
                    fileupload._name = name[:max_length]
            if self.instance:
                self.instance.mimetype = fileupload.content_type
        return fileupload
    
    def clean(self):
        """ Insert the filename as title if no title is given """
        title = self.cleaned_data.get('title', None)
        if not title:
            fileupload = self.cleaned_data.get('file', None)
            if fileupload:
                self.cleaned_data.update({'title': fileupload._name},)
                self.errors.pop('title', None)
        return super(_FileForm, self).clean()
    
        
FileForm = get_form(_FileForm, attachable=False)


class FileListForm(forms.Form):

    # required=False to handle the validation in the view
    select = forms.MultipleChoiceField(required=False)
