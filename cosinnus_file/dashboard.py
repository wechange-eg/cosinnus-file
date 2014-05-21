# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from cosinnus.utils.dashboard import DashboardWidget, DashboardWidgetForm

from cosinnus_file.models import FileEntry


class LatestFileEntryForm(DashboardWidgetForm):
    amount = forms.IntegerField(label="Amount", initial=5, min_value=0,
        help_text="0 means unlimited", required=False)


class Latest(DashboardWidget):

    app_name = 'file'
    form_class = LatestFileEntryForm
    model = FileEntry
    title = _('Latest Files')
    user_model_attr = None  # No filtering on user page
    widget_name = 'latest'

    def get_data(self):
        if self.request.user.is_authenticated():
            count = int(self.config['amount'])
            qs = self.get_queryset().select_related('group').order_by('-created').all()
            if count != 0:
                qs = qs[:count]
        else:
            qs = []
        data = {
            'rows': qs,
            'no_data': _('No files'),
        }
        return render_to_string('cosinnus_file/widgets/latest.html', data)

    def get_queryset(self):
        qs = super(Latest, self).get_queryset()
        return qs.filter(is_container=False)
