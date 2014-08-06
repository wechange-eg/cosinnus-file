'''
Created on 05.08.2014

@author: Sascha
'''
from django.utils.translation import ugettext_lazy as _

from cosinnus.views.mixins.filters import CosinnusFilterSet
from cosinnus.forms.filters import AllObjectsFilter, SelectCreatorWidget
from cosinnus_file.models import FileEntry


class FileFilter(CosinnusFilterSet):
    creator = AllObjectsFilter(label=_('Created By'), widget=SelectCreatorWidget)
    
    class Meta:
        model = FileEntry
        fields = ['creator']
        order_by = (
            ('-created', _('Newest Created')),
            ('_filesize', _('Smallest Files')),
            ('-_filesize', _('Largest Files')),
        )
    
    def get_order_by(self, order_value):
        return super(FileFilter, self).get_order_by(order_value)
    