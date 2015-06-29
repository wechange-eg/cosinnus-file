'''
Created on 05.08.2014

@author: Sascha
'''
from django.utils.translation import ugettext_lazy as _

from cosinnus.views.mixins.filters import CosinnusFilterSet
from cosinnus.forms.filters import AllObjectsFilter, SelectCreatorWidget,\
    DropdownChoiceWidget
from cosinnus_file.models import FileEntry
from django_filters.filters import ChoiceFilter
from django.core.exceptions import ImproperlyConfigured


FILE_TYPE_FILTER_CHOICES = [
    ('images', _('Pictures')), 
    ('documents', _('Documents')), 
    ('audio', _('Audio Files')), 
    ('videos', _('Videos')),
]

class FileTypeFilter(ChoiceFilter):
    
    file_extensions = {
        'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        'documents': ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlx', 'xlsx', 'rtf', 'txt', 'odt', 'odf', 'odp'],
        'audio': ['wav', 'mp3', 'ogg'],
        'videos': ['mov', 'avi', 'mp4', 'mpeg', 'mpg', 'flv'],
    }
    
    def filter(self, qs, value):
        if not value:
            return qs
        if not value in self.file_extensions:
            raise ImproperlyConfigured('FileType filer %s not found!' % value) 
        
        result_qs = self.model._default_manager.none()
        for ext in self.file_extensions.get(value):
            filter_value = ('.%s' % ext, 'iendswith')
            result_qs |= super(FileTypeFilter, self).filter(qs, filter_value)
            
        return result_qs
    

class FileFilter(CosinnusFilterSet):
    creator = AllObjectsFilter(label=_('Created By'), widget=SelectCreatorWidget)
    filetype = FileTypeFilter(label=_('File Type'), name="_sourcefilename", choices=FILE_TYPE_FILTER_CHOICES, widget=DropdownChoiceWidget)
    
    class Meta:
        model = FileEntry
        fields = ['creator', 'filetype']
        order_by = (
            ('title', _('File Name')),
            ('-title', _('File Name (descending)')),
            ('-created', _('Newest Created')),
            ('_filesize', _('Smallest Files')),
            ('-_filesize', _('Largest Files')),
        )
    
    def get_order_by(self, order_value):
        return super(FileFilter, self).get_order_by(order_value)
    