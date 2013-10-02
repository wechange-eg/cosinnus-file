# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms.models import ModelForm

from cosinnus.utils.forms import BootstrapTagWidget

from cosinnus_file.models import FileEntry


class FileForm(ModelForm):

    class Meta:
        model = FileEntry
        fields = ('name', 'file', 'note', 'tags')
        widgets = {
            'tags': BootstrapTagWidget(),
        }


class FileListForm(forms.Form):
    select = forms.MultipleChoiceField(required=False)  # required=False to handle this validation in the view
